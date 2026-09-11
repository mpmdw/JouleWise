OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd0d-a2cd-7e93-a5e3-8f598c75fa7c
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

== YOUR ASSIGNED DIRECTION (energy-nutrition-label) ==
An energy nutrition label for consumer LLM inference: a reporting-standard proposal (named boundary, floor, calibration state, stack identity) grounded in the measured attribution limit — the leaderboard critique made constructive.

codex
I’ll develop the “energy nutrition label” as a standards-and-evidence paper that reuses the MVP’s measured instrument limits and the full D-117 dataset. I’m reading the required sources first, then I’ll quantify the smallest modest extensions that make the label proposal empirically testable without crossing the frozen single-request boundary.
exec
/bin/zsh -lc 'git status --short --branch && wc -l docs/paper/draft-v1.md CLAIMS_STATUS.md docs/decision_log.md docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md docs/strategy/2026-08-06-impressiveness-roadmap.md docs/research_question_registry.md docs/research_question_bank.md docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md AGENT_PLAN.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
     286 AGENT_PLAN.md
   13976 total

exec
/bin/zsh -lc "sed -n '1,240p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
/bin/zsh -lc "sed -n '1,240p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
exec
/bin/zsh -lc "sed -n '1,260p' docs/strategy/2026-08-06-impressiveness-roadmap.md; sed -n '1,180p' docs/research_question_registry.md; sed -n '1,120p' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '1,194p' docs/paper/draft-v1.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '1,220p' CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
/bin/zsh -lc "rg -n '"'^## D-117|''^### D-117|D-117'"' docs/decision_log.md | tail -20" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7088:> allowance correction STAND and bind the D-117 mints.
7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

exec
/bin/zsh -lc "sed -n '7507,7605p' docs/decision_log.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '171,340p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '1,170p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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


exec
/bin/zsh -lc "sed -n '341,520p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
/bin/zsh -lc "sed -n '1,260p' docs/strategy/2026-08-06-impressiveness-roadmap.md; sed -n '1,180p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
/bin/zsh -lc "sed -n '1,180p' docs/research_question_registry.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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
The existing governance strongly favors a standards contribution, but with a crucial ceiling: this can propose and validate a label schema; it cannot claim to be “the standard,” and it cannot launch a public cross-device leaderboard from one unit. I’m now checking the full question bank for earlier kills and wording constraints so the proposal turns that limitation into a falsifiable audit study rather than a branding exercise.
exec
/bin/zsh -lc "sed -n '1,280p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
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

exec
/bin/zsh -lc "sed -n '281,560p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '561,840p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:

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

exec
/bin/zsh -lc "sed -n '841,1120p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
/bin/zsh -lc "rg -n '"'^## (ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next)|''^# Mission M0|''^## Mission M0|''^## (Current Queue|Do-Not-Do-Yet)'"' RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md AGENT_PLAN.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
TASK_QUEUE.md:306:## Current Queue
RUN_STATE.md:2039:## ACTIVE_STOP_CARD
RUN_STATE.md:2178:## Current Project Status
RUN_STATE.md:2739:## Known Workspace State

exec
/bin/zsh -lc "rg -n '"'^## .*Next|Do.Not|DO.NOT|Do Not|What Is'"' RUN_STATE.md TASK_QUEUE.md | tail -30; sed -n '2039,2250p' RUN_STATE.md; sed -n '2739,2840p' RUN_STATE.md; sed -n '50,140p' docs/agent_playbook.md; sed -n '306,475p' TASK_QUEUE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
RUN_STATE.md:2806:## Historical Next-Work Snapshot (superseded 2026-07-15)
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
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

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

### 2N.1 `RunContext` seam + raw evidence

- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
  ~line 160) but no method writes into it, and adapters never see the
  bundle path — so a real telemetry adapter cannot honor D-002 ("raw
  file retained verbatim").
- Change: implement **D-024** (already decided — read it first): an
  immutable `RunContext` dataclass (config, clock, run_id, bundle_path,
  raw_dir, logs_dir, outputs_dir, optional node_role=None) constructed
  by the controller after bundle creation and passed to adapter
  lifecycle methods (exact placement — per-method parameter vs
  construction-time — is yours to pin; record the choice as a D-024
  amendment note). Add `RunBundleWriter.raw_path(name)`/`write_raw` as
  the writer-side counterpart (validated, collision-checked). Update
  `docs/contracts/adapter_contracts.md` in the same run. Do NOT hand
  adapters the writer itself — D-024 rejects that option; context is
  data, not capability.
- Tests: mock telemetry writes a fixture raw file via the context;
  bundle contains it; immutability (no overwrite after finalize); the
  no-raw-output mock path still passes; mocks ignore unused context
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
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |

### [QUIET-MAC] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |

### [AGENT] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| A0 | P2-035 | P3 Research Expansion | READY | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

### Shelved task records

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| A1 | P2-036 | P3 Research Expansion | SHELVED — trigger: P2-023 (HumanEval import smoke (P2-023) lands) | Second-benchmark-family source session: pick and freeze the second import family with licensing/contamination/shape discipline; MMLU/tinyBenchmarks remain rejected as first. | Named family plus frozen subset manifest passing claims_lint --mode pack. Evidence: Named family with license/provenance fields; Frozen subset manifest passing claims_lint --mode pack. Authority: [Import-family campaign pack](docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md). Acceptance: [P2-036 acceptance](docs/process/state_kernel.json). Note: SHELF per C-026 meeting; FLORES language-set decision (D-046/B6) may share the session. |
| A8 | SEC5A-REMOTE-01 | P2 Next Slice | SHELVED — trigger: SEC5A-remote-ruling (Ed ruling ratifying the §5A remote-attestation amendment before it takes effect), QUIET-GUARD-01 (QUIET-GUARD-01 lands (the guard supplies the amendment's programmatic substrate)); GATES close: SEC5A-remote-ruling | §5A remote-attestation amendment (ruling-requiring): programmatic checks (adapter negotiation, network time, process inventory, display state) plus Ed remote attestation replace physical-presence §5A when hardware state is already correct; hands required only on check failure. | The §5A amendment is drafted with the four programmatic checks plus Ed remote attestation substituting for physical presence when hardware state is already correct, and is ratified by an Ed ruling before taking effect. Evidence: Amendment drafted against the §5A home document with the physical-presence substitution conditions stated exactly; Programmatic checks specified and implemented: adapter negotiation, network time, process inventory, display state; Ed remote attestation step defined; hands required only on check failure; Ed ruling recorded ratifying the amendment. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [SEC5A-REMOTE-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). Shelved with the guard's shelved commits: the programmatic substrate this amendment needed lived in the dropped watcher/handoff scope. |
| A9 | WO-T3-VIS-01 | P1 Phase Gate | SHELVED | t3-thread-bridge (full council — new adapter): audited wrapper dispatching thread.create and turn.start so delegated Sol rounds appear as REAL t3 threads (phone-visible fleet). Probes plus spec first, then implementation. | An audited t3-thread-bridge wrapper dispatches thread.create and turn.start so delegated Sol rounds appear as real, phone-visible t3 threads, landed probes-then-spec-then-implementation under full council. Evidence: Probes establish thread.create and turn.start dispatch semantics before any implementation; Spec ratified before implementation begins; Audited wrapper carries the standard audit trail for dispatched rounds; A delegated Sol round demonstrably appears as a real t3 thread visible from the phone; Full council convened (new-adapter trigger). Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [WO-T3-VIS-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). t3-thread-bridge shelved: phone-visible delegated rounds are the exact convenience the descope declines to pay for. Reopen only on Ed's word. |
| A26 | P2-048 | P2 Next Slice | SHELVED — trigger: P1-003 (external wall-meter decision supplies a usable device path) | Implement the conditional external-meter importer and boundary-calibrate CLI for the already-designed Q6 and D-018 bridge. | The existing Q6 and D-018 bridge design is implemented with bound metadata, synchronization, paired windows, calibration fit, held-out gate, floor identity, and refusal reasons. Evidence: External-meter importer; boundary-calibrate CLI; Designed refusal reasons and held-out gate. Authority: [Hardening adjudication C9](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-048 acceptance](docs/process/state_kernel.json). Fence: Implement the existing bridge design; do not create a duplicate design contract (Hardening adjudication C9). Note: Conditional on P1-003 selecting an available meter path. |
| A27 | CI-003 | P3 Research Expansion | SHELVED — trigger: G6 (G6 reference milestone is complete) | Evaluate post-reference developer polish: console entry point, macOS install/import CI, Ruff, and measured coverage reporting. | Post-reference developer polish is adopted only from observed need; thresholds follow measurement rather than precedent. Evidence: Observed baseline justifies each adopted tool; Console entry point and macOS job only if useful; Measured coverage policy. Authority: [Hardening adjudication C10](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [CI-003 acceptance](docs/process/state_kernel.json). |
| A28 | DOC-010 | P4 Polish | SHELVED — trigger: DOC-008-proven-in-use (DOC-008 state kernel (merged PR #60, 2026-07-11) is proven in use), G6 (G6 reference milestone is complete) | Audit non-authoritative historical material for bounded relocation after DOC-008 proves the state kernel. | A post-DOC-008 audit relocates only non-authoritative history while preserving paths or redirects, citations, decision authority, and link integrity. Evidence: Only non-authoritative historical material moves; Paths or redirects preserve citations; Decision and evidence links remain intact. Authority: [Hardening adjudication C11](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [DOC-010 acceptance](docs/process/state_kernel.json). Fence: Do not move cited evidence, decisions, council records, or authoritative histories (Hardening adjudication C11). |
| Q7 | T3-CHAR-PAIR-01 | P1 Phase Gate | SHELVED | App-up vs app-down idle-capture characterization pair (NON-CLAIM): decide whether t3 resident processes (server, helpers, cloudflared) pollute the quiet-mac measurement floor; unlocks the app-adjacent window-operation question. Runnable next quiet night; blocked by nothing. | A matched app-up vs app-down idle-capture pair with custody and roots fully separate from any claim chain yields a recorded NON-CLAIM verdict on whether t3 resident processes pollute the measurement floor. Evidence: App-down idle capture collected on a quiet night under standard idle-capture conditions; App-up idle capture collected under matched conditions with the t3 resident processes (server, helpers, cloudflared) running; Recorded comparison verdict, labelled NON-CLAIM, deciding the app-adjacent window-operation question; Custody and roots separate from any claim chain; shares no baselines, calibration, or NEG-8 evidence. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [T3-CHAR-PAIR-01 acceptance](docs/process/state_kernel.json). Fence: NON-CLAIM characterization only: outputs enter no claim custody root and share no baselines, calibration, or NEG-8 evidence with any claim chain (t3-doctrine gate synthesis: characterization pair is custody-separate from any claim chain). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). Both arms shelved: the app-UP r03 re-capture and the app-DOWN arm existed to decide app-adjacent window admissibility, which the descope moots. Reopen only on Ed's word. |

<!-- END GENERATED: state-kernel current-queue -->

exec
/bin/zsh -lc "sed -n '213,305p' TASK_QUEUE.md; sed -n '306,390p' TASK_QUEUE.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

exec
/bin/zsh -lc "rg -n -i 'nutrition label|energy label|model card|leaderboard|reporting standard|standards contribution|boundary table|label schema|reporting schema' docs CLAIMS_STATUS.md PROJECT_STATUS.md AGENT_PLAN.md | head -200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/strategy/2026-08-06-impressiveness-roadmap.md:128:- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
docs/reviews/2026-07-09-scientific-rigor-review.md:42:   boundary table with forbidden cross-boundary language, the claims
docs/reviews/2026-07-09-scientific-rigor-review.md:277:JouleWise is scientifically useful if it is presented as a boundary-honest measurement instrument plus a controlled workload suite, not as a universal leaderboard. Its strongest design choice is that it treats raw evidence as primary: config, metadata, event logs, power traces, outputs, reducer results, and telemetry logs are bundled and re-reducible. That is the right instinct for energy measurement, and it aligns with the methodological tradition of JouleSort, SPEC/MLPerf-style power work, and newer ML energy tooling: define the system boundary, preserve logs, report uncertainty, and avoid uncalibrated cross-system winners.
docs/reviews/2026-07-09-scientific-rigor-review.md:544:   boundary table, claims ladder with forbidden language, pre-registered
docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md:16:  leaderboard join, or benchmark-score normalization.
docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md:42:| Disqualifiers + not-resolvable conditions | Live/latest split, missing source license/hash, missing source row hash, unmatched shape/output policy, no P2-023 HumanEval plumbing, no active item/level floor for L2, or any attempt to infer accuracy, pass@k, coding capability, leaderboard standing, or benchmark score. |
docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md:53:| multiplicity_rule | Holm within FAM-C5I2-DIFFICULTY-ASSOCIATION for predeclared repeated-bundle L2 stratum contrasts when such bundles exist; otherwise exploratory/no-confirmatory-inference for L1 association summaries. BH item-level sweeps at q=0.10 are limited to source-provided quarantined metadata summaries; no JouleWise correctness scoring, accuracy, pass@k, leaderboard, benchmark-score normalization, or item-energy inference. |
docs/campaign_packs/c5_i_1_i_2_i_5_import_family.md:239:- Do not make pass@k, accuracy, coding-capability, leaderboard, benchmark-score
docs/reviews/2026-07-08-technical-merit-review.md:43:7. **Cross-device breadth-seeking local-LLM deployers** -- the largest nominal audience and the least served: six bundles, two models, one machine, and a self-imposed leaderboard bar pending cross-lab replication. They remain with Intelligence-per-Watt/Bench360-class tables; JouleWise offers depth-with-uncertainty before it offers broad cross-device coverage.
docs/campaign_packs/c5_i_4_harness_overhead_floor.md:36:| Disqualifiers + not-resolvable conditions | `external_markers_unsupported`, missing external results hash, unpaired markers, non-monotonic timestamps, markers outside measured window, overlapping items undeclared, failed strict validation, no matching floor row, same/calibrated boundary absent for L2 comparison, or accuracy/pass@k/leaderboard interpretation. |
docs/campaign_packs/c5_i_4_harness_overhead_floor.md:170:- Do not join JouleWise energy to accuracy, pass@k, leaderboard standing, or
docs/research_question_bank.md:390:accuracy interpretation, no leaderboard join, no pass@k-energy ratio, and
docs/research_question_bank.md:399:- leaderboard integration.
docs/research_question_bank.md:407:- public energy model-card leaderboard before cross-lab replication.
docs/research_question_bank.md:1052:  bundles + configs. Gates every public-facing application (leaderboard,
docs/research_question_bank.md:1077:5. **Practitioner energy model cards / leaderboard** — joules/token with
docs/research_question_bank.md:1087:8. **Bundle contract as a standards contribution** — the run-bundle
docs/research_question_bank.md:1088:   layout + boundary table + strict validator packaged as a proposed
docs/phase_4/related_work_draft.md:43:   re-reducible artifact — not leaderboard summary numbers.
docs/phase_4/related_work_draft.md:193:boundary table), D-013 (controller co-residency and idle-baseline
docs/phase_4/related_work_draft.md:334:requests. It publishes results on the public ML.ENERGY Leaderboard and
docs/phase_4/related_work_draft.md:346:hardware), raw power-trace/event-log run bundles instead of leaderboard
docs/phase_4/related_work_draft.md:443:where joules go rather than reporting single leaderboard numbers) but
docs/phase_4/related_work_draft.md:561:(D-018) with a named boundary table, on device classes where a uniform
docs/phase_4/related_work_draft.md:586:publicly auditable there (caveats: the headline leaderboard surfaces only
docs/phase_4/related_work_draft.md:688:  (Stage 4.4) inherits the D-018 boundary table; Section 6 Claim 1's
docs/phase_4/phase_4_exit_checklist.md:15:| 4.4 results draft | required | pending | findings for Q1/Q2/Q3; limitations cover boundary table, co-residency, exercised fallbacks, network conditions | `docs/phase_4/results_draft.md` |
docs/phase_4/phase_4_plan.md:13:- Boundary table: D-018 / methodology Measurement Boundaries section
docs/phase_4/phase_4_plan.md:274:  than leaderboard numbers, and split-inference energy on local
docs/site_src/results.html:5:  <p class="lede">This is a measurement ledger, not a leaderboard. Gross energy
docs/process/state_kernel.json:2135:          "rule": "Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim"
docs/site_src/index.html:8:  a prettier leaderboard. It is a defensible way to ask where the joules went.</p>
docs/decision_log.md:973:fixable post hoc; the boundary table converts an implicit comparability
docs/decision_log.md:981:inherits the boundary table.
docs/decision_log.md:2267:   pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
docs/decision_log.md:2269:   11-entry list, which is authoritative): leaderboard integration, live
docs/decision_log.md:2275:   independent replication, public energy leaderboards before cross-lab
docs/council_log.md:304:   energy labels and carbon accounting are a natural use. Attack
docs/council_log.md:319:4. **Cross-device leaderboard / public model cards — SCOPED to an
docs/council_log.md:321:   scores, public leaderboard on identical hardware. Attack (examiner
docs/council_log.md:436:- Public cross-device leaderboards before wall calibration + cross-lab
docs/contracts/token_normalization.md:106:| Tokenizer-blind "energy per token" leaderboard language | Ranking stacks without naming tokenizer identity and request energy. | "tokenizer-scoped companion metrics for [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size], reported beside request energy." |
docs/risk_register.md:152:  matters; D-018's boundary table makes results honest without a meter.
docs/JouleWise_Hardening_Proposal.md:76:- A hardware leaderboard.
docs/JouleWise_Hardening_Proposal.md:107:- Build a public leaderboard.
docs/JouleWise_Hardening_Proposal.md:604:| P3 | New imports/leaderboard/site breadth | Low marginal value before adoption | External demand exists |
docs/JouleWise_Hardening_Proposal.md:782:This is more interesting than another per-device leaderboard because it tests an interaction: **quantization × hardware/runtime**. A result such as “4-bit wins on stack A, 8-bit wins on stack B, and FP16 remains competitive on stack C at short outputs” would be both useful and appropriately bounded.
docs/JouleWise_Hardening_Proposal.md:911:- A leaderboard.
docs/contracts/adapter_contracts.md:123:- Leaderboard standing from joined accuracy(theirs)+energy(ours).
docs/research_question_registry.md:84:| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
docs/research_question_registry.md:111:| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
docs/research_question_registry.md:113:| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
docs/site/roadmap.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Roadmap - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html" class="active">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <section class="observatory-hero"> <div class="kicker">Roadmap</div> <h1>Queue rank is the flight plan.</h1> <p class="lede">The current queue is parsed from the exact live table headers in <code>TASK_QUEUE.md</code>. Lane filters are progressive enhancement.</p> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </section> <section class="flight-plan"> <div class="next-two"><span class="card-label">Next two</span><strong class="mono">P1-008 -> P2-027</strong><p>P1-008 runs first, then P2-027.</p></div> <div class="lane-filters" aria-label="Filter queue by lane"> <button type="button" data-lane-filter="all" aria-pressed="true" class="active">All</button> <button type="button" data-lane-filter="QUIET-MAC" aria-pressed="false">Quiet Mac</button> <button type="button" data-lane-filter="AGENT" aria-pressed="false">Agent</button> <button type="button" data-lane-filter="ED-EXTERNAL" aria-pressed="false">Ed</button> </div> </section> <section class="queue-stack"><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E1</span><span class="mono task-code">P1-008</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</h2> <details><summary>Acceptance</summary><p>Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: <a href="docs/milestones.md">Milestones + R-012</a>. Acceptance: <a href="docs/process/state_kernel.json">P1-008 acceptance</a>. Note: R-012 is the biggest active management risk for an undergrad timeline.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E2</span><span class="mono task-code">P2-027</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party.</h2> <details><summary>Acceptance</summary><p>Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-020 + C-027 NEG-9</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-027 acceptance</a>. Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E3</span><span class="mono task-code">P1-001</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Capture supervisor approval and scope notes.</h2> <details><summary>Acceptance</summary><p>Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: <a href="docs/risk_register.md">R-001</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E4</span><span class="mono task-code">P1-003</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method.</h2> <details><summary>Acceptance</summary><p>Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: <a href="docs/decision_log.md">D-018/C-003</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Elevated value: gates Q6 boundary sensitivity (C-003).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E5</span><span class="mono task-code">P1-004</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method.</h2> <details><summary>Acceptance</summary><p>Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: <a href="docs/risk_register.md">R-011</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Partial.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="ED-EXTERNAL"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#E6</span><span class="mono task-code">P1-006</span><span class="status-chip">READY</span><span class="lane-chip lane-ed-external">ED-EXTERNAL</span></div> <p class="status-note">READY</p> <h2>Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L).</h2> <details><summary>Acceptance</summary><p>Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: <a href="docs/phase_2/hardware_slice_implementation_guide.md">Remote gate / NV-GATE-2</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q1</span><span class="mono task-code">P2-015</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">PARTIAL; READY</p> <h2>Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</h2> <details><summary>Acceptance</summary><p>Reducer-0.5.2/0.6.2 strict-valid calibration bundles; per-metric floor_abs_j and floor_cmp_j; governed idle uncertainty retained; calibration manifest hash cited by later reports. Evidence: Versioned strict-valid calibration bundles; Per-metric/window-class floor_abs_j + floor_cmp_j; Calibration manifest hash cited by later reports. Authority: <a href="docs/phase_2/detection_floor.md">D-054 + detection floor spec</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Fence: Claim-bearing collection requires fresh 59-pulse protocol-v3 calibration BRACKETING the window (consumed max(B_pre,B_post)); floor artifacts are claim-licensing only from same-custody-session governed extraction until FLOOR-BIND-01 closes (D-078 clause 8 (L1) + bracketing ruling). Note: PR #79 instrument repair and PR #85 SCREEN+BUDGET rules are merged; the start gate is one clean quiet window executed per docs/phase_2/window_runbook.md.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q2</span><span class="mono task-code">P2-006</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors measured first)</p> <h2>Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.</h2> <details><summary>Acceptance</summary><p>Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: <a href="docs/phase_2/phase_2_plan.md">Phase 2 plan + analysis plans</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Note: Software interpretation gates are satisfied; execution remains blocked until P2-015 Window-A floors complete.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q3</span><span class="mono task-code">P2-010</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (quiet-window tail available after floors)</p> <h2>P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail.</h2> <details><summary>Acceptance</summary><p>joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: <a href="docs/contracts/analysis_plans.md">AP-5 + affine stream log</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-010 acceptance</a>. Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q4</span><span class="mono task-code">P2-019</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (Window-A baselines size n)</p> <h2>q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).</h2> <details><summary>Acceptance</summary><p>Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: <a href="docs/contracts/analysis_plans.md">AP-1</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-019 acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q5</span><span class="mono task-code">P2-020</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (Window-A baselines size n)</p> <h2>Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts.</h2> <details><summary>Acceptance</summary><p>Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: <a href="docs/contracts/analysis_plans.md">AP-6 + D-046</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-020 acceptance</a>. Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q6</span><span class="mono task-code">P2-012</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-006 (identification-core runs after Window A)</p> <h2>Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases.</h2> <details><summary>Acceptance</summary><p>Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: <a href="docs/contracts/analysis_plans.md">AP-4 + D-039/D-040</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-012 acceptance</a>. Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q8</span><span class="mono task-code">P2-046B</span><span class="status-chip">READY</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">READY</p> <h2>Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts.</h2> <details><summary>Acceptance</summary><p>Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C6</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-046B acceptance</a>. Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="QUIET-MAC"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#Q9</span><span class="mono task-code">P2-047B</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-quiet-mac">QUIET-MAC</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors exist), P2-047A (frozen controller-overhead harness exists)</p> <h2>Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict.</h2> <details><summary>Acceptance</summary><p>Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047B acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A0</span><span class="mono task-code">P2-035</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (P2-015 detection floors measured)</p> <h2>RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).</h2> <details><summary>Acceptance</summary><p>Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: <a href="docs/specs/rq_energy_variance_design.md">RQ-ENERGY-VARIANCE candidate design</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-035 acceptance</a>. Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A3</span><span class="mono task-code">FLOOR-BIND-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</h2> <details><summary>Acceptance</summary><p>Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: <a href="docs/decision_log.md">D-078 clause 8 (confirmation round 9, registered limitation L1)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-BIND-01 acceptance</a>. Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A4</span><span class="mono task-code">AXI-SB-ADAPTER</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.</h2> <details><summary>Acceptance</summary><p>The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: <a href="docs/specs/axi/sb_static_batch_verdict.md">AXI-SB verdict document (supported; mint-on-supported follow-on)</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SB-ADAPTER acceptance</a>. Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A6</span><span class="mono task-code">AXI-SD</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Prepare the matched dense/MoE pair proposal with the consult&#x27;s pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT.</h2> <details><summary>Acceptance</summary><p>A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016&#x27;s cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-D</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SD acceptance</a>. Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A7</span><span class="mono task-code">AXI-SE</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (P2-015 publishes Window-A floors before AXI analysis plans are finalized)</p> <h2>Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult&#x27;s floor and ownership closures.</h2> <details><summary>Acceptance</summary><p>The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A&#x27;s gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-E</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SE acceptance</a>. Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A16</span><span class="mono task-code">P3-000</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — R-003 (user approves the 3.0.2 installs (R-003))</p> <h2>KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8).</h2> <details><summary>Acceptance</summary><p>Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: <a href="docs/decision_log.md">D-035/D-036</a>. Acceptance: <a href="docs/phase_3/phase_3_exit_checklist.md">Phase 3 exit checklist</a>. Note: 3.0.1 complete and merged (PR #9, replay_supported).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A17</span><span class="mono task-code">P2-022</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041))</p> <h2>Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported).</h2> <details><summary>Acceptance</summary><p>3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/contracts/adapter_contracts.md">Adapter contract</a>. Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A18</span><span class="mono task-code">P2-023</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded)</p> <h2>HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy.</h2> <details><summary>Acceptance</summary><p>Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/research_question_bank.md">RQ bank import-smoke design</a>. Fence: No pass@k, accuracy, or capability claim (D-041).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A19</span><span class="mono task-code">P2-024</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (2M reductions identify floor/MDE headroom), P2-015 (Window-A floors measured)</p> <h2>Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC].</h2> <details><summary>Acceptance</summary><p>Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: <a href="docs/research_question_bank.md">C-015 + RQ bank</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-024 acceptance</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A21</span><span class="mono task-code">P3-001b</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (2M affine coefficients exist)</p> <h2>Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049).</h2> <details><summary>Acceptance</summary><p>AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: <a href="docs/decision_log.md">D-048/D-049</a>. Acceptance: <a href="docs/contracts/analysis_plans.md">Analysis plans (split row)</a>.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A22</span><span class="mono task-code">P2-004</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: P1-001</p> <h2>Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding.</h2> <details><summary>Acceptance</summary><p>Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: <a href="docs/decision_log.md">D-016</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Provisional small-model pick 2026-07-06 opens 2G.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A23</span><span class="mono task-code">P2-005</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES live_promotion: P1-006</p> <h2>Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute.</h2> <details><summary>Acceptance</summary><p>Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: <a href="docs/specs/c027/nv-gate-2_live_promotion.md">NV-GATE-2 live-promotion spec</a>. Acceptance: <a href="docs/phase_1/2k_live_verification_checklist.md">2K live verification checklist</a>. Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A24</span><span class="mono task-code">P2-016</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-006 (the 2M corpus exists)</p> <h2>Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.</h2> <details><summary>Acceptance</summary><p>Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-011 ledger + C-027 (post-2M umbrella)</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-016 acceptance</a>. Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A25</span><span class="mono task-code">P2-047A</span><span class="status-chip">BLOCKED</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">BLOCKED — P2-015 (Window-A floors exist before overhead design is frozen)</p> <h2>Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes.</h2> <details><summary>Acceptance</summary><p>A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047A acceptance</a>. Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A29</span><span class="mono task-code">DOC-008-REFLECTION</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6.</h2> <details><summary>Acceptance</summary><p>Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A30</span><span class="mono task-code">DOC-008-STATUS</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8.</h2> <details><summary>Acceptance</summary><p>Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A31</span><span class="mono task-code">DOC-008-INTAKE</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9.</h2> <details><summary>Acceptance</summary><p>Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake and procedure reconciliation</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake reconciliation</a>. Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p4"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A32</span><span class="mono task-code">DOC-008</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS</p> <h2>Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked.</h2> <details><summary>Acceptance</summary><p>Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 state-kernel specification</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 required outcomes</a>. Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A33</span><span class="mono task-code">P2-050</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2.</h2> <details><summary>Acceptance</summary><p>Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: <a href="docs/run_reports/2026-07-11-c028-continuation.md">C-028 dissent-record queue candidates</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-050 acceptance</a>. Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A34</span><span class="mono task-code">TOOL-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers.</h2> <details><summary>Acceptance</summary><p>All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: <a href="docs/run_reports/2026-07-13-bridge-v11.md">Bridge v1.1 wrapper and session operations record</a>. Acceptance: <a href="docs/process/state_kernel.json">TOOL-01 acceptance</a>. Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A35</span><span class="mono task-code">AUD-FOLLOWUPS</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Close the ULTRA comparison audit&#x27;s accepted small residue in one bounded agent task: WO-012&#x27;s owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage.</h2> <details><summary>Acceptance</summary><p>The ULTRA comparison audit&#x27;s five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012&#x27;s owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/report.md">Comprehensive-audit close-out and accepted-residue list</a>. Acceptance: <a href="docs/process/state_kernel.json">AUD-FOLLOWUPS acceptance</a>. Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A36</span><span class="mono task-code">AUD-WO-033</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: P2-006</p> <h2>After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path.</h2> <details><summary>Acceptance</summary><p>The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-033</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-033</a>. Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A37</span><span class="mono task-code">AUD-WO-034</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: PHASE-3-SPLIT-SCHEDULED</p> <h2>At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable.</h2> <details><summary>Acceptance</summary><p>When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-034</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-034</a>. Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A38</span><span class="mono task-code">AUD-WO-035</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED</p> <h2>Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks.</h2> <details><summary>Acceptance</summary><p>The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-035</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-035</a>. Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A39</span><span class="mono task-code">AUD-WO-036</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED</p> <h2>When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior.</h2> <details><summary>Acceptance</summary><p>Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-036</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-036</a>. Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A40</span><span class="mono task-code">AUD-WO-037</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED</p> <h2>Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path.</h2> <details><summary>Acceptance</summary><p>Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-037</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-037</a>. Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A41</span><span class="mono task-code">AUD-WO-038</span><span class="status-chip">READY;</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED</p> <h2>At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition.</h2> <details><summary>Acceptance</summary><p>At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-038</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-038</a>. Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p3"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A42</span><span class="mono task-code">AUD-WO-039</span><span class="status-chip">PARTIAL</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED</p> <h2>At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review.</h2> <details><summary>Acceptance</summary><p>The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-039</a>. Acceptance: <a href="docs/reviews/2026-07-13-comprehensive-audit/register.jsonl">Comprehensive-audit register WO-039</a>. Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A43</span><span class="mono task-code">CUSTODY-HARDEN-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel.</h2> <details><summary>Acceptance</summary><p>Close the PR #85 gauntlet&#x27;s deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: <a href="docs/council_log.md">C-033 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)</a>. Acceptance: <a href="docs/process/state_kernel.json">CUSTODY-HARDEN-01 acceptance</a>. Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A44</span><span class="mono task-code">CAL-REBRACKET-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Implement the governed max-bracket prospective re-reduction flow (authenticated bracket max, sealed reduction manifest, basis revision, consumption binding), then re-reduce and extract windows a10/a9.</h2> <details><summary>Acceptance</summary><p>Close the max-bracket consumption gap: post&gt;pre calibration windows (a coin flip) are structurally unconsumable until the D-078-required prospective re-reduction flow exists. Evidence: A governed prospective-reduction flow re-reduces a complete 37-occurrence evaluation basis under the authenticated max(B_pre,B_post), never a caller-supplied scalar; Derived summaries land in a dedicated custody directory with a hash-sealed manifest binding source/raw/stored-summary/reducer/calibration/policy/derived hashes; Whole-window verification and extraction select the exact revised basis and reject incomplete, mixed, duplicated, or latest-wins artifacts; Regressions cover omitted references, substituted summaries, scalar inflation, partial coverage, conflicting basis rows; Windows a10 and a9 re-reduced and consumed; a10 phase floors extracted with drift allowances. Authority: <a href="docs/decision_log.md">D-078 bracketing ruling (max(B_pre,B_post)) + 2026-07-25 collection-night consult (S1 design in job tmp bracket_consult.md)</a>. Acceptance: <a href="docs/process/state_kernel.json">CAL-REBRACKET-01 acceptance</a>. Fence: The earliest valid causal post-calibration is the operative post; later valid captures never replace it, and retrying a valid calibration to seek a smaller bound is forbidden. (No-verdict-shopping ruling). Note: Minted 2026-07-25 from the first collection night under the merged rules: a9+a10 both PASSED verdicts at mint; consumption refused calibration_bracket_exceeds_minted_bound (post 25.046ms &gt; pre 24.879ms minted). Operator deviation recorded: post-cal pulse-failure retry outside the run-book&#x27;s clock-anchor-only retry shape (evidence preserved; earliest-valid-causal selection unaffected).</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A45</span><span class="mono task-code">FLOOR-LABEL-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Convert admissible_set_uncertainty_dominates_point_floor from hard refusal to a labelled claim path (floor_source names the dominant term; point floor retained as repeatability diagnostic), after Ed ratifies the D-078 amendment.</h2> <details><summary>Acceptance</summary><p>Attribution-limited floors become claimable and labelled, so instrument-limited windows publish an honest floor instead of refusing. Evidence: D-078 amendment ratified by Ed BEFORE any code softening (closed-registry channel); Extraction emits a labelled claim-path floor with floor_source naming the dominant uncertainty term; Point (repeatability) floor preserved and reported separately as a diagnostic; Single-count discipline recorded: effective clearable effect = floor + claim-side bound; neither may be optimized away; a10 phase cells extract as labelled attribution-limited floors. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-LABEL-01 acceptance</a>. Fence: No code change to the dominating-uncertainty gate before Ed ratifies the D-078 amendment; the registry channel is mandatory. (D-054 floor semantics / closed-registry amendment rule). Note: Minted 2026-07-25. D-054 defines the floor as a practical prediction bound on FALSE OBSERVED EFFECTS, not a repeatability statistic; the corner-widened maximum satisfies that definition. GATE: Ed ratifies the amendment first — do not soften the gate in code before ratification.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p1"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A46</span><span class="mono task-code">FLOOR-WORKLOAD-SIZING-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes.</h2> <details><summary>Acceptance</summary><p>Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-WORKLOAD-SIZING-01 acceptance</a>. Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A47</span><span class="mono task-code">FLOOR-COMMONMODE-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially.</h2> <details><summary>Acceptance</summary><p>The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-COMMONMODE-01 acceptance</a>. Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell&#x27;s 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article><article class="lane-card" data-lane="AGENT"> <div class="priority-band p2"></div> <div class="lane-main"> <div class="lane-head"><span class="lane-rank mono">#A48</span><span class="mono task-code">PHASE-SHARE-ESTIMAND-01</span><span class="status-chip">READY</span><span class="lane-chip lane-agent">AGENT</span></div> <p class="status-note">READY</p> <h2>Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box.</h2> <details><summary>Acceptance</summary><p>Treating each phase&#x27;s anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: <a href="docs/decision_log.md">2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)</a>. Acceptance: <a href="docs/process/state_kernel.json">PHASE-SHARE-ESTIMAND-01 acceptance</a>. Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost.</p></details> <span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span> </div> </article></section> <section class="interlock"><h2>Do not do yet</h2><ul><li>(satisfied 2026-06-12) The mock bundle/reducer path and report generator now exist; dashboard/report work is no longer blocked.</li> <li>(satisfied 2026-06-12) The mock lifecycle is runnable, so live MLX/powermetrics implementation may proceed once its hardware gates open (P1-002 + D-016); follow <code>docs/phase_2/hardware_slice_implementation_guide.md</code>.</li> <li>(resolved 2026-06-12) Hailo feasibility has a verdict (<code>unsupported_workload</code>); do not implement a Hailo backend — report it as an applicability finding.</li> <li>Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in D-008; implementation waits).</li> <li>Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware pairings, or borrow-window scheduling before 2M baselines and the Stage 3.0 verdicts exist (C-007 wording fix; was previously stated as a blanket Phase 3 hold that contradicted the queue).</li> <li>Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the rehearsed runbook exist (R-006).</li> <li>Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has produced data.</li> <li>Do not close D-016 (model selection) without P1-001 supervisor scope or an explicit user go-ahead.</li> <li>(satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own gates (D-016 + <code>[mac]</code> install; privileged sample + D-004 sudoers) open — build on the post-2N seams (RunContext raw evidence, D-026 markers, D-027 rail rows, 2N.3 observed-token fallback).</li></ul><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></section> <section class="timeline-rail"><h2>Completed reel</h2><div class="timeline-node"><span class="mono">2026-07-18</span><strong>CODEX-BRIDGE-PET</strong><p>Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>P2-015-SMOKE</strong><p>Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>P2-038</strong><p>Close the production-uncertainty live tail with a true MLX + <code>/usr/bin/powermetrics</code> production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup</p></div> <div class="timeline-node"><span class="mono">2026-07-17</span><strong>AXI-SC</strong><p>AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict <code>unsupported_for_joulewise</code> (external draft: <code>event_observability</code>; native MTP: <code>native_mtp_generation</code>); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>AXI-SB</strong><p>AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict <code>supported</code> (mlx-lm 0.31.3 BatchGenerator path; true B&gt;1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>SPLIT-AP</strong><p>Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>SITE-02</strong><p>Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step)</p></div> <div class="timeline-node"><span class="mono">2026-07-16</span><strong>AXI-SA</strong><p>AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last)</p></div> <div class="timeline-node"><span class="mono">2026-07-15</span><strong>AXI-S0</strong><p>AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh)</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>SITE-01</strong><p>Site capsule under the 1 MiB Lakebed cap + live redeploy</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>P2-028</strong><p>Response-hash determinism gate (<code>joulewise determinism-gate</code>)</p></div> <div class="timeline-node"><span class="mono">2026-07-13</span><strong>P2-049</strong><p>analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3)</p></div><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></section> <script>
docs/report_src/chapters/03_background_and_related_work.md:59:inference energy as a diagnosis problem rather than a single leaderboard
docs/site/risk_register.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Risk Register - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#summary">Summary</a> <a href="#r-001-supervisor-approval-delayed-or-scope-shifts">R-001: Supervisor approval delayed or scope shifts</a> <a href="#r-002-powermetrics-sudo-workflow-not-approved-on-measurement-mac">R-002: powermetrics sudo workflow not approved on measurement Mac</a> <a href="#r-003-mlx-install-or-model-load-failure-on-mac">R-003: MLX install or model-load failure on Mac</a> <a href="#r-004-kv-persist-resume-unsupported-in-a-target-runtime">R-004: KV persist/resume unsupported in a target runtime</a> <a href="#r-005-llama-cpp-cache-files-not-portable-across-machines-backends">R-005: llama.cpp cache files not portable across machines/backends</a> <a href="#r-006-3080-ti-borrow-window-slips-or-shrinks">R-006: 3080 Ti borrow window slips or shrinks</a> <a href="#r-007-no-wall-meter-available">R-007: No wall meter available</a> <a href="#r-008-orin-telemetry-inaccessible">R-008: Orin telemetry inaccessible</a> <a href="#r-009-hailo-cannot-run-llm-shaped-workloads">R-009: Hailo cannot run LLM-shaped workloads</a> <a href="#r-010-controller-as-dut-contamination-on-mac-runs">R-010: Controller-as-DUT contamination on Mac runs</a> <a href="#r-011-benchmark-network-cannot-be-isolated">R-011: Benchmark network cannot be isolated</a> <a href="#r-012-schedule-five-phases-vs-fixed-academic-deadlines">R-012: Schedule: five phases vs fixed academic deadlines</a> <a href="#r-013-thermal-throttling-confounds-measurements">R-013: Thermal throttling confounds measurements</a> <a href="#r-014-model-weights-become-unavailable-or-gated">R-014: Model weights become unavailable or gated</a> <a href="#r-015-schema-changes-after-data-collection-starts">R-015: Schema changes after data collection starts</a> <a href="#r-016-measurement-corpus-loss-runs-has-no-backup-path">R-016: Measurement-corpus loss (runs/ has no backup path)</a> <a href="#r-017-repo-lives-on-icloud-synced-desktop-eperm-lock-recurrence">R-017: Repo lives on iCloud-synced Desktop (EPERM lock recurrence)</a> <a href="#r-018-the-agent-loop-itself-as-a-schedule-and-scope-risk">R-018: The agent loop itself as a schedule and scope risk</a></aside> <div class="doc-wrap doc-source-docs-risk-register-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>docs/risk_register.md</code></p> <div class="provenance-plate"><span class="source-chip" title="docs/risk_register.md · commit dbd8137"><span class="source-file">docs/<wbr>risk_register.md</span><span class="source-commit">commit dbd8137</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>Risk Register</h1> <p>Living register of risks that could sink, delay, or weaken the capstone. Review at the start of every phase and whenever a trigger fires; update statuses at the end of substantial runs alongside <code>RUN_STATE.md</code>.</p> <p>Conventions:</p> <ul> <li>Likelihood/Impact: low / medium / high, judged against the current phase.</li> <li>Trigger: the observable event that means the risk is materializing.</li> <li>Mitigation: what we do <em>now</em> to reduce likelihood or impact.</li> <li>Fallback: what we do <em>if it happens</em> - every fallback must preserve a publishable result, even if smaller.</li> <li>Owner: <code>user</code> for actions needing human/lab/supervisor access, <code>agent</code> for repo work.</li> </ul> <h2 id="summary">Summary</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Risk</th> <th>Phase</th> <th>Likelihood</th> <th>Impact</th> <th>Status</th> </tr> </thead> <tbody><tr> <td>R-001</td> <td>Supervisor approval delayed or scope shifts</td> <td>1</td> <td>medium</td> <td>high</td> <td>open</td> </tr> <tr> <td>R-002</td> <td>powermetrics sudo workflow not approved on measurement Mac</td> <td>2</td> <td>low</td> <td>high</td> <td>closed-residual</td> </tr> <tr> <td>R-003</td> <td>MLX install or model-load failure on Mac</td> <td>2</td> <td>low</td> <td>medium</td> <td>closed-residual</td> </tr> <tr> <td>R-004</td> <td>KV persist/resume unsupported in a target runtime</td> <td>3</td> <td>medium</td> <td>high</td> <td>open</td> </tr> <tr> <td>R-005</td> <td>llama.cpp cache files not portable across machines/backends</td> <td>3</td> <td>medium</td> <td>high</td> <td>open</td> </tr> <tr> <td>R-006</td> <td>3080 Ti borrow window slips or shrinks</td> <td>3</td> <td>medium</td> <td>medium</td> <td>open</td> </tr> <tr> <td>R-007</td> <td>No wall meter available</td> <td>1-4</td> <td>medium</td> <td>medium</td> <td>open</td> </tr> <tr> <td>R-008</td> <td>Orin telemetry inaccessible</td> <td>2-3</td> <td>medium</td> <td>low</td> <td>open</td> </tr> <tr> <td>R-009</td> <td>Hailo cannot run LLM-shaped workloads</td> <td>1</td> <td>high</td> <td>low</td> <td>open (by design)</td> </tr> <tr> <td>R-010</td> <td>Controller-as-DUT contamination on Mac runs</td> <td>2</td> <td>high (unmitigated)</td> <td>medium</td> <td>mitigated by D-013</td> </tr> <tr> <td>R-011</td> <td>Benchmark network cannot be isolated</td> <td>3</td> <td>medium</td> <td>medium</td> <td>open</td> </tr> <tr> <td>R-012</td> <td>Schedule: five phases vs fixed academic deadlines</td> <td>all</td> <td>medium</td> <td>high</td> <td>open</td> </tr> <tr> <td>R-013</td> <td>Thermal throttling confounds measurements</td> <td>2-4</td> <td>medium</td> <td>medium</td> <td>mitigated by D-014</td> </tr> <tr> <td>R-014</td> <td>Model weights become unavailable or gated</td> <td>2+</td> <td>low</td> <td>medium</td> <td>open</td> </tr> <tr> <td>R-015</td> <td>Schema changes after data collection starts</td> <td>2+</td> <td>low</td> <td>high</td> <td>mitigated</td> </tr> <tr> <td>R-016</td> <td>Measurement-corpus loss (<code>runs/</code> has no backup path)</td> <td>2-5</td> <td>low</td> <td>high</td> <td>mitigated (2026-07-10: iCloud Drive destination live, fresh restore test passed; re-verify before each window — eviction caveat)</td> </tr> <tr> <td>R-017</td> <td>Repo on iCloud-synced Desktop (EPERM lock recurrence)</td> <td>all</td> <td>low</td> <td>medium</td> <td>mitigated (repo moved 2026-07-05; residual: session launch paths)</td> </tr> <tr> <td>R-018</td> <td>Agent-loop self-expansion consumes calendar without grader-facing output</td> <td>all</td> <td>medium</td> <td>high</td> <td>mitigated-in-policy (D-060 RATIFIED 2026-07-10; enforcement = queue discipline + spend guardrails, WO-022/R2, <code>docs/orchestration.md</code> §Spend guardrails)</td> </tr> </tbody></table></div> <h2 id="r-001-supervisor-approval-delayed-or-scope-shifts">R-001: Supervisor approval delayed or scope shifts</h2> <ul> <li>Phase: 1. Likelihood: medium. Impact: high (wrong deliverable built).</li> <li>Trigger: Phase 2 implementation slices ready to start (2A-2F complete) with P1-001 still open; or any supervisor communication contradicting <code>AGENT_PLAN.md</code> scope.</li> <li>Status note (2026-07-05): the first trigger fired 2026-06-12 (2A-2F completed with P1-001 still open). The mitigation is holding as designed - all work since has been hardware-independent and harness-shaped (mock slice, docs, Slice 2N is next and is also ungated) - and the fallback (&quot;continue only mock/local work; hardware purchases/borrows blocked-on-approval&quot;) is effectively in force.</li> <li>Mitigation: the queue keeps P1-001 ranked first; all work until approval stays hardware-independent and harness-shaped (valuable under any scope); the Phase 1 exit checklist lists the exact questions to put to the supervisor so one meeting can close the gate.</li> <li>Fallback: if approval stalls past mock-slice completion, continue only mock/local work and mark every hardware purchase or borrow decision blocked-on-approval.</li> <li>Owner: user.</li> </ul> <h2 id="r-002-powermetrics-sudo-workflow-not-approved-on-measurement-mac">R-002: powermetrics sudo workflow not approved on measurement Mac</h2> <ul> <li>Phase: 2. Likelihood: low (user controls the machine; a local auth session needs rescheduling - the planned 2026-06-10 slot passed without one). Impact: high (no Mac telemetry = no flagship vertical slice).</li> <li>Status: closed-residual (2026-07-08). The working Mac slice completed 2G/2H/2I on 2026-07-06 with privileged powermetrics capture and strict-valid bundles; revisit for new macOS/MLX/powermetrics versions or new Mac hardware.</li> <li>Trigger: scoped sudoers rule (D-004) cannot be installed, or privileged sample capture fails after the auth session.</li> <li>Mitigation: D-004 defines a minimal, single-binary sudoers rule with the exact line documented in the Phase 1 exit checklist&#39;s instrumentation section; interactive-sudo manual fallback documented for attended runs.</li> <li>Fallback: attended runs with interactive sudo (operator present per experiment); if even that is unacceptable, the Mac becomes runtime-supported/telemetry-blocked and the first real slice moves to the first available CUDA target - recorded as a finding, not hidden.</li> <li>Owner: user (install rule), agent (pre-check + structured failure).</li> </ul> <h2 id="r-003-mlx-install-or-model-load-failure-on-mac">R-003: MLX install or model-load failure on Mac</h2> <ul> <li>Phase: 2. Likelihood: low. Impact: medium (delays flagship slice).</li> <li>Status: closed-residual (2026-07-08). The working Mac slice completed 2G/2H/2I on 2026-07-06 with MLX generation and strict-valid bundles; revisit for new MLX/mlx-lm versions or new Mac hardware.</li> <li>Trigger: <code>pip install mlx mlx-lm</code> fails, or the chosen model (D-016) has no working MLX artifact.</li> <li>Mitigation: install into a dedicated venv with versions recorded in run bundles; model criteria (D-016) require known MLX availability before selection; smoke-test load before scheduling measurement sessions.</li> <li>Fallback: llama.cpp with the Metal backend as the Mac runtime (already a planned runtime for split portability under D-015); the MLX adapter then becomes optional rather than flagship.</li> <li>Owner: agent (with user approving installs).</li> </ul> <h2 id="r-004-kv-persist-resume-unsupported-in-a-target-runtime">R-004: KV persist/resume unsupported in a target runtime</h2> <ul> <li>Phase: 3. Likelihood: medium overall (high for vLLM file-based replay, low for llama.cpp, low-medium for mlx-lm). Impact: high if unmitigated - this is the project&#39;s central feasibility risk.</li> <li>Trigger: a Stage 3.0 spike returns <code>replay_unsupported</code> for a runtime needed by a planned pairing.</li> <li>Mitigation: D-015&#39;s feasibility ladder - spikes run <em>before</em> any split hardware time is scheduled; pairings are planned only on runtimes with <code>replay_supported</code> verdicts; the synthetic transfer microbenchmark (Stage 3.1) is independent of all runtime cooperation and guarantees a crossover dataset.</li> <li>Fallback: analytical composition - measured prefill energy (node A) + measured synthetic transfer energy (payload sized by the KV model) + measured decode energy (node B) bounds the split cost honestly; the report states the composition method explicitly.</li> <li>Owner: agent.</li> </ul> <h2 id="r-005-llama-cpp-cache-files-not-portable-across-machines-backends">R-005: llama.cpp cache files not portable across machines/backends</h2> <ul> <li>Phase: 3. Likelihood: medium (session files are version- and model-sensitive; cross-backend CUDA-save -&gt; Metal-load is unverified). Impact: high for <em>heterogeneous</em> pairings specifically.</li> <li>Trigger: Stage 3.0.2&#39;s cross-machine restore test fails or produces divergent output.</li> <li>Mitigation: the spike tests cross-machine restore explicitly, with pinned identical llama.cpp versions and identical GGUF files on both ends, before any heterogeneous experiment is scheduled.</li> <li>Fallback: restrict offline-replay pairings to same-platform pairs (GPU-&gt;GPU in the borrow window, Orin-&gt;Orin); cover heterogeneous pairs with the analytical composition (R-004 fallback); report the portability finding itself - it is a legitimate disaggregation-practicality result.</li> <li>Owner: agent.</li> </ul> <h2 id="r-006-3080-ti-borrow-window-slips-or-shrinks">R-006: 3080 Ti borrow window slips or shrinks</h2> <ul> <li>Phase: 3. Likelihood: medium. Impact: medium (loses GPU-&gt;GPU pairing, not the phase).</li> <li>Trigger: window not scheduled by Phase 3 Stage 3.2 completion; or window arrives before split tooling is ready.</li> <li>Mitigation: all split tooling reaches rehearsed-on-available-hardware state before the window (the Phase 3 plan keeps a borrow-window runbook so borrow time is execution-only, no debugging); calendar mapping task (P1-008) makes the window a tracked date.</li> <li>Fallback: GPU-&gt;GPU pairing drops to single-GPU prefill/decode phase decomposition plus analytical composition; 3050&lt;-&gt;Orin and Orin&lt;-&gt;Orin remain.</li> <li>Owner: user (scheduling), agent (runbook readiness).</li> </ul> <h2 id="r-007-no-wall-meter-available">R-007: No wall meter available</h2> <ul> <li>Phase: 1-4. Likelihood: medium. Impact: medium (boundary calibration and Pi/Hailo coverage lost; per-target results stand).</li> <li>Trigger: P1-003 resolves &quot;unavailable&quot;.</li> <li>Mitigation: P1-003 is a Phase 1 gate precisely so this resolves before it matters; D-018&#39;s boundary table makes results honest without a meter.</li> <li>Fallback: report within-target comparisons (always boundary-consistent) as primary; flag cross-target absolute comparisons with the boundary caveat; targets with no platform telemetry (Pi) become telemetry-unavailable findings.</li> <li>Owner: user.</li> </ul> <h2 id="r-008-orin-telemetry-inaccessible">R-008: Orin telemetry inaccessible</h2> <ul> <li>Phase: 2-3. Likelihood: medium (rail sysfs paths vary by L4T version). Impact: low (one target of several).</li> <li>Trigger: P1-006 evidence shows neither INA3221 sysfs nor tegrastats usable.</li> <li>Mitigation: two candidate mechanisms documented before hardware time; wall-meter fallback if R-007 resolves positively.</li> <li>Fallback: Orin runs runtime-only (latency/throughput) marked telemetry-unavailable, or drops to a stretch target.</li> <li>Owner: user (access), agent (adapter).</li> </ul> <h2 id="r-009-hailo-cannot-run-llm-shaped-workloads">R-009: Hailo cannot run LLM-shaped workloads</h2> <ul> <li>Phase: 1. Likelihood: high. Impact: low - <em>by design</em>: the plan treats Hailo as a feasibility investigation whose negative verdict is itself a reportable applicability finding.</li> <li>Status: <strong>realized as expected, 2026-06-12</strong> — verdict <code>unsupported_workload</code>. The trigger fired (a non-<code>supported</code> verdict), the by-design mitigation held, and the outcome is the publishable applicability finding the plan anticipated. No schedule impact.</li> <li>Trigger: feasibility checklist closes with any non-<code>supported</code> verdict. (Fired 2026-06-12.)</li> <li>Mitigation: none needed; the verdict-code structure in the Phase 1 exit checklist&#39;s Hailo section makes the outcome publishable either way. Do not spend implementation effort on a Hailo backend (the verdict is now recorded; the standing do-not-do-yet rule becomes &quot;report, don&#39;t implement&quot;).</li> <li>Fallback: Pi 5 CPU-only llama.cpp with wall-meter telemetry becomes an optional low-power data point if the meter exists; otherwise Pi/Hailo appears only in the applicability table.</li> <li>Owner: user (device access), agent (verdict documentation - done).</li> </ul> <h2 id="r-010-controller-as-dut-contamination-on-mac-runs">R-010: Controller-as-DUT contamination on Mac runs</h2> <ul> <li>Phase: 2. Likelihood: high if unmitigated. Impact: medium (biased flagship numbers).</li> <li>Status: mitigated by D-013 (idle baseline includes resident quiescent controller; deferred logging; blocking wait during measured window).</li> <li>Trigger (residual): SSH-controlled comparison runs (once transport exists) show a delta beyond run-to-run variance.</li> <li>Fallback: move Mac headline measurements to remote-controlled runs.</li> <li>Owner: agent.</li> </ul> <h2 id="r-011-benchmark-network-cannot-be-isolated">R-011: Benchmark network cannot be isolated</h2> <ul> <li>Phase: 3. Likelihood: medium (campus/home network constraints unknown until P1-004 closes). Impact: medium (noisy transfer measurements).</li> <li>Trigger: P1-004 topology answer shows shared links only.</li> <li>Mitigation: prefer direct node-to-node cabling (no switch) for 1GbE/2.5GbE point-to-point tests - removes the isolation question entirely for two-node experiments; record link conditions per run in the bundle.</li> <li>Fallback: run sweeps off-hours, repeat n&gt;=5, report observed throughput alongside nominal link speed (the bundle already records measured throughput per D-008&#39;s transfer block).</li> <li>Owner: user (hardware), agent (recording).</li> </ul> <h2 id="r-012-schedule-five-phases-vs-fixed-academic-deadlines">R-012: Schedule: five phases vs fixed academic deadlines</h2> <ul> <li>Phase: all. Likelihood: medium. Impact: high (capstones fail by calendar, not by code).</li> <li>Trigger: any phase exceeding its (to-be-set) calendar budget; colloquium or report dates announced (P1-008) leaving less runway than the plan assumes.</li> <li>Mitigation: P1-008 maps phases to real dates as soon as the user supplies them (<code>docs/milestones.md</code> holds the skeleton); every phase defines a hardware-independent floor and a descope ladder so cutting is a decision, not a scramble.</li> <li>Descope ladder (worst-case minimum viable capstone, in cut order):<ol> <li>Drop live split (3.3) - already stretch.</li> <li>Drop 10GbE and one model size.</li> <li>Drop heterogeneous replay pairs (keep synthetic transfer + analytical composition).</li> <li>Drop Orin/Pi targets (keep Mac + one CUDA).</li> <li>Floor: mock harness + Mac vertical slice + homogeneous baselines + synthetic interconnect sweep + analytical split model. This is still a complete, defensible benchmark-plus-study.</li> </ol> </li> <li>Owner: user (dates), agent (floor discipline).</li> </ul> <h2 id="r-013-thermal-throttling-confounds-measurements">R-013: Thermal throttling confounds measurements</h2> <ul> <li>Phase: 2-4. Likelihood: medium (high on passively-cooled Orin/Pi). Impact: medium (rep-to-rep drift, biased late reps).</li> <li>Status: mitigated by D-014 (idle-power recovery gate between reps, thermal_drift_c in measurement quality, interleaved ordering) - residual risk on targets without thermal sensors.</li> <li>Trigger: thermal_drift_c trending across reps, or cooldown cap hits recorded in bundles.</li> <li>Fallback: longer cooldowns, active cooling notes recorded in run metadata, or excluding throttled reps <em>with documented cause</em> per D-014.</li> <li>Owner: agent.</li> </ul> <h2 id="r-014-model-weights-become-unavailable-or-gated">R-014: Model weights become unavailable or gated</h2> <ul> <li>Phase: 2+. Likelihood: low. Impact: medium (mid-project model swap breaks comparability).</li> <li>Trigger: chosen model&#39;s hub entry gated/removed; license terms change.</li> <li>Mitigation: D-016 requires mirroring chosen weights to local storage immediately on selection, with revisions and hashes recorded.</li> <li>Fallback: promote the recorded fallback candidate; re-run affected baselines (the config hash separates old/new data cleanly).</li> <li>Owner: agent.</li> </ul> <h2 id="r-015-schema-changes-after-data-collection-starts">R-015: Schema changes after data collection starts</h2> <ul> <li>Phase: 2+. Likelihood: low. Impact: high (existing bundles unreadable or silently misread).</li> <li>Status: mitigated structurally.</li> <li>Mitigation: schema_version field exists from v0.1; D-008 plans the only anticipated breaking-shape change (v0.2) <em>before</em> split data collection; output-schema additions are additive-only (the JSON schema does not forbid additional properties); <code>validate-bundle</code> pins what a valid bundle means per version.</li> <li>Trigger: any proposed non-additive change to a schema with bundles already on disk.</li> <li>Fallback: a dated migration note in this repo plus a one-shot migration script; never edit bundles in place (they are evidence).</li> <li>Owner: agent.</li> </ul> <h2 id="r-016-measurement-corpus-loss-runs-has-no-backup-path">R-016: Measurement-corpus loss (runs/ has no backup path)</h2> <ul> <li>Phase: 2-5. Likelihood: low. Impact: high (the dataset behind every claim is a gitignored directory on one disk; a disk failure or an errant delete erases the evidence the defense rests on, and hardware re-collection needs access windows that may not recur).</li> <li>Trigger: first real (non-mock) bundle written; any data-affecting incident (disk error, iCloud eviction anomaly, accidental delete).</li> <li>Mitigation: before the first real measurement session (gate on 2I data collection, tracked as queue task P0-002), define and record the backup protocol here: destination (external disk and/or cloud location outside the repo), cadence (after every measurement session), method (rsync of <code>runs/</code> plus experiment manifests), and a restore test performed once. Configs + manifests already make re-collection well-defined; backups make it unnecessary.</li> <li><strong>Protocol recorded (2026-07-06, P0-002 closed interim).</strong> Destination: <code>~/JouleWise-backup</code> — a user-directed INTERIM location on the same disk (&quot;cursory... I&#39;ll handle that later&quot;); it protects against errant deletes but not disk failure, so the user still owes an external/cloud destination for full mitigation. Cadence: after every measurement session. Method: <code>scripts/backup_runs.sh [RUNS_DIR] [DEST]</code> (rsync -a, never <code>--delete</code>; dated UTC log line per invocation appended to <code>DEST/backup.log</code>). Restore test performed 2026-07-06: mock bundle backed up, restored to a temp dir, <code>validate-bundle</code> green on the restored copy. Swapping in the final destination is a one-argument change (or edit the script default) plus one fresh restore test.</li> <li><strong>Protocol upgraded (2026-07-10/11, P0-003 closed; addendum 2026-07-16 closing a summary-row/body drift found by the resumption audit).</strong> The interim same-disk destination above is superseded: the external destination is iCloud Drive, live with a fresh backup + restore test passed (evidence: <code>docs/run_reports/2026-07-11-c028-continuation.md</code> §11, &quot;The P0-003 iCloud measurement-corpus backup and restore gate is satisfied&quot;). The 2026-07-06 entry above is retained as history. Standing caveat: iCloud eviction — re-verify the destination is materialized (fresh restore test) before each measurement window.</li> <li>Fallback: re-run affected experiments from their configs (the config hash separates old/new data cleanly per D-005/D-010); report any unrecoverable gap honestly in the exclusion log.</li> <li>Owner: user (destination/media), agent (protocol doc + restore test).</li> </ul> <h2 id="r-017-repo-lives-on-icloud-synced-desktop-eperm-lock-recurrence">R-017: Repo lives on iCloud-synced Desktop (EPERM lock recurrence)</h2> <ul> <li>Phase: all. Likelihood: low (mitigated; was high while on Desktop). Impact: medium (blocks work sessions mid-run; small integrity risk around eviction during writes).</li> <li>Status: <strong>mitigated 2026-07-05</strong> - the repo moved off the synced Desktop (current canonical path: <code>~/code/JouleWise</code>; the interim <code>~/code/CapstoneRivoire/Capstone</code> path recorded here was itself later renamed - corrected 2026-07-09, C-027). P0-001 complete; git + suite verified green at the new path. Residual exposure: agent sessions launched from the stale Desktop path (delete the leftover <code>~/Desktop/CapstoneRivoire</code> husk after relaunching from the new path), and any future placement of repo or <code>runs/</code> data under an iCloud-synced directory - do not.</li> <li>Trigger: any <code>Operation not permitted</code> on read/readdir inside the repo with the iCloud file provider (<code>bird</code>) active.</li> <li>History: first incident 2026-06-12 (documented in <code>RUN_STATE.md</code>); recurred 2026-07-05 mid-run - <code>docs/</code>, <code>joulewise/</code>, <code>tests/</code>, <code>.git</code>, and the repo root EPERM-locked intermittently during an active iCloud full-sync, clearing and re-locking per subtree. Both incidents match iCloud &quot;Optimize Mac Storage&quot; behavior on <code>~/Desktop/</code>. The move landed the same day as the second incident.</li> <li>Fallback: if a lock ever strikes again, wait for it to clear (both incidents did), then re-verify with the test suite before continuing; the remote (<code>origin/main</code>) bounds code loss to the working tree.</li> <li>Owner: user (launch paths), agent (post-lock verification discipline).</li> </ul> <h2 id="r-018-the-agent-loop-itself-as-a-schedule-and-scope-risk">R-018: The agent loop itself as a schedule and scope risk</h2> <ul> <li>Phase: all. Likelihood: medium. Impact: high (capstones fail by calendar, R-012).</li> <li>Registered by C-027 (NEGSPACE lens finding accepted in council): the multi-agent workflow can remain locally productive - packs, registries, meta-process, site work - while the graded deliverable path (rubric, report source, backup, real corpus, figures) stays starved. Same-day evidence at registration: ~6M tokens of breadth work vs six real corpus bundles, no report source, same-disk backup.</li> <li>Trigger: an agent-heavy work block that produces neither a new real evidence bundle nor a report/figure increment.</li> <li>Mitigation: D-060 depth-before-breadth stop line (RATIFIED by Ed 2026-07-10) extended by the WO-022/R2 spend guardrails (<code>docs/orchestration.md</code> §Spend guardrails, 2026-07-15); RPT-001 vertical slice; the C-027 correctness rows ranked ahead of all breadth work.</li> <li>Owner: lead (queue discipline + guardrail checkpoints), Ed (HARD bands and structure).</li> </ul> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/risk_register.md · commit dbd8137 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/site/results.html:17:</header> <main> <section class="readme-hero measurement-hero"> <div class="kicker">Measurements · after method, evidence, and gates</div> <p class="readme-eyebrow">Numbers with their basis attached.</p> <h1>What the instrument<br>has observed so far.</h1> <p class="lede">This is a measurement ledger, not a leaderboard. Gross energy is the comparison headline. Idle-subtracted energy is shown only as a within-device secondary view. Strict-valid collection and claim readiness are reported separately.</p> <div class="provenance-plate"><span class="source-chip" title="docs/decision_log.md · commit 1af9f92 + uncommitted"><span class="source-file">docs/<wbr>decision_log.md</span><span class="source-commit">commit 1af9f92 + uncommitted</span></span> <span class="source-chip" title="docs/contracts/claims_ladder.md · commit db150a0"><span class="source-file">docs/<wbr>contracts/<wbr>claims_ladder.md</span><span class="source-commit">commit db150a0</span></span> <span class="source-chip" title="docs/site_src/results.html · commit 632d9eb"><span class="source-file">docs/<wbr>site_src/<wbr>results.html</span><span class="source-commit">commit 632d9eb</span></span></div> </section> <section class="band tight readme-section"> <div class="kicker">Basis rule · D-067</div> <div class="basis-banner"> <div><strong>Headline basis</strong><span>gross energy within the named <code>powermetrics</code> SoC-rail boundary</span></div> <div><strong>Secondary view</strong><span>idle-subtracted energy, within-device only; never used to rank devices or configurations</span></div> <div><strong>Phase energy</strong><span>gross only, per D-032</span></div> </div> </section> <section class="band readme-section"> <div class="kicker">Legacy descriptive baseline · Apple M3 Max</div> <h2>The first live Mac observations.</h2> <p class="section-intro">These are legacy L1 preliminary observations from the initial MLX + <code>powermetrics</code> vertical slice, before the governed baseline campaign.</p> <div class="measurement-grid"> <article class="readout"><div class="card-label">Gross request energy · headline basis</div><div class="val">≈47.2<span class="unit">J/request</span></div><div class="sub">M3 Max · powermetrics SoC rails · gross measured interval</div></article> <article class="readout cyan"><div class="card-label">Idle-subtracted request energy · secondary</div><div class="val">≈44.4<span class="unit">J/request</span></div><div class="sub">same device only · activity above measured idle baseline</div></article> <article class="readout cyan"><div class="card-label">Idle-subtracted output-token energy · secondary</div><div class="val">86.8<span class="unit">mJ/token mean</span></div><div class="sub">observed range 79–90 mJ/token · same-device secondary view</div></article> <article class="readout plain"><div class="card-label">Companion performance metric</div><div class="val">257<span class="unit">token/s</span></div><div class="sub">throughput; not an energy-basis measurement</div></article> </div> <div class="provenance-plate"><span class="source-chip" title="README.md · commit 1af9f92"><span class="source-file">README.md</span><span class="source-commit">commit 1af9f92</span></span></div> </section> <section class="band readme-section"> <div class="kicker">Verified Window-A floor extraction</div> <h2>How large a change must be before this run can resolve it?</h2> <p class="section-intro">Each value below is a false-effect guard floor from the verified extraction. “Absolute” describes repeat scatter; “comparative” uses ABBA blocks and may be larger under drift. A later effect must clear the applicable gate <em>and</em> every other claim gate.</p> <div class="table-scroll"> <table class="ledger measurement-table"> <thead><tr><th>window</th><th>basis</th><th>absolute floor</th><th>comparative / governing gate</th></tr></thead> <tbody> <tr><td>mid request</td><td>gross · headline</td><td>0.527197 J</td><td>0.909237 J</td></tr> <tr><td>mid request</td><td>idle-subtracted · within-device secondary</td><td>0.536632 J</td><td>0.894215 J</td></tr> <tr><td>prefill phase</td><td>gross · phase basis</td><td>see extraction</td><td>1.738940 J governing gate</td></tr> <tr><td>decode phase</td><td>gross · phase basis</td><td>see extraction</td><td>1.026892 J governing gate</td></tr> <tr><td>suite item</td><td>gross · headline</td><td>see extraction</td><td>4.922865 J governing gate</td></tr> <tr><td>suite level</td><td>gross · headline</td><td>see extraction</td><td>24.618735 J governing gate</td></tr> </tbody> </table> </div> <div class="evidence-warning"><strong>Collection-complete is not claim-ready.</strong> Every floor bundle was strict-valid and collection-usable, but every one was also claim-evidence flagged. Clock-bound and in-window-sample flags were universal; several comparative cells also show drift or cooldown concerns. These floors are honestly reported calibration evidence pending the named adjudication gates.</div> <div class="provenance-plate"><span class="source-chip" title="docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895"><span class="source-file">docs/<wbr>process_traces/<wbr>2026-07-17-floor-extraction/<wbr>extraction-verified.json</span><span class="source-commit">commit b28c895</span></span></div> </section> <section class="band readme-section"> <div class="kicker">Interpretation</div> <h2>What can—and cannot—be said today.</h2> <div class="claim-grid measurement-claims"> <div><span class="status-chip">Supported</span><p>The harness has made real, descriptive, gross-basis and labeled idle-secondary observations on the named Mac and telemetry boundary.</p></div> <div><span class="status-chip amber">Calibration only</span><p>The verified floor values describe the observed campaign conditions; they do not by themselves establish a model or configuration difference.</p></div> <div><span class="status-chip danger">Not supported</span><p>No cross-device ranking, broad content-neutrality result, or split-inference energy win is claimed from these measurements.</p></div> </div> <p><a href="research.html#floor">Use the interactive floor gate →</a></p> </section> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/site_src/results.html · commit 632d9eb · README.md · commit 1af9f92 · docs/decision_log.md · commit 1af9f92 + uncommitted · docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895 · docs/contracts/claims_ladder.md · commit db150a0 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/specs/suite_next/decision_review_log.md:97:energy, judge scoring, and leaderboard metrics require separate contracts and
docs/specs/suite_next/decision_review_log.md:150:   claims, or benchmark leaderboard territory?
docs/specs/suite_next/instruction_tuning_spec.md:26:- no intelligence-per-joule or leaderboard claims
docs/specs/suite_next/instruction_tuning_spec.md:178:  leaderboard territory and needs a separate evaluation policy.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2161:./docs/site/task_queue.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Task Queue - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#intake-rule-for-new-tasks">Intake Rule For New Tasks</a> <a href="#priority-scale">Priority Scale</a> <a href="#ranking-factors">Ranking Factors</a> <a href="#ready-shelf-rule">Ready/Shelf Rule</a> <a href="#machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</a> <a href="#historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</a> <a href="#completed-queue-items">Completed Queue Items</a> <a href="#shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</a> <a href="#current-do-not-do-yet-list">Current Do-Not-Do-Yet List</a> <a href="#queue-maintenance">Queue Maintenance</a> <a href="#current-queue">Current Queue</a> <a href="#active-global-work-selection-gates">Active Global Work-Selection Gates</a></aside> <div class="doc-wrap doc-source-task-queue-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>TASK_QUEUE.md</code></p> <div class="provenance-plate"><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise Task Queue</h1> <p>This is the live queue for JouleWise work. When the user gives a new task, first triage it here instead of assuming it should happen immediately.</p> <h2 id="intake-rule-for-new-tasks">Intake Rule For New Tasks</h2> <p>For every new user task:</p> <ol> <li>Read <code>RUN_STATE.md</code>.</li> <li>Read this file.</li> <li>Check <code>git status --short --branch</code>.</li> <li>Review the last 2-3 commits with <code>git log --oneline --decorate -3</code>.</li> <li>Check relevant handoffs in <code>docs/run_reports/</code>.</li> <li>If <code>RUN_STATE.md</code> contains an ACTIVE <code>ACTIVE_STOP_CARD</code>, that card outranks this queue. Execute or preserve the card&#39;s resume/cleanup instructions before considering any lower-ranked work.</li> <li>Decide whether the task is:<ul> <li>urgent workspace hygiene,</li> <li>Phase 1 evidence work,</li> <li>Phase 2 implementation prep,</li> <li>later-phase research work,</li> <li>documentation/reporting,</li> <li>or unrelated/new scope.</li> </ul> </li> <li>Place or update the task in the queue with priority, rationale, evidence, and blockers.</li> <li>If executing it now, say why it outranks the current top task.</li> <li>Closure rule (D-023): a row may move to Completed only after the corresponding phase exit-checklist matrix row already shows the same status with dated evidence, and the Completed row&#39;s evidence cell must cite that matrix row (file + item id). If no matrix row exists for the work, say so explicitly in the evidence cell.</li> </ol> <h2 id="priority-scale">Priority Scale</h2> <ul> <li><strong>P0 Safety</strong>: prevents accidental data loss, bad commits, broken handoffs, or corrupted repo state.</li> <li><strong>P1 Phase Gate</strong>: required to close the current phase or unblock the next phase responsibly.</li> <li><strong>P2 Next Slice</strong>: next implementation slice after current phase gates are adequately planned or closed.</li> <li><strong>P3 Research Expansion</strong>: useful experiment or feature, but not needed for current gate.</li> <li><strong>P4 Polish</strong>: quality-of-life, dashboard polish, formatting, cleanup, or presentation work.</li> </ul> <h2 id="ranking-factors">Ranking Factors</h2> <p>Rank higher when a task:</p> <ul> <li>Prevents accidental loss or bad Git history.</li> <li>Produces evidence for the current phase exit checklist.</li> <li>Removes ambiguity for multiple later steps.</li> <li>Is required before physical hardware time is spent.</li> <li>Is cheap to verify and reduces future confusion.</li> <li>Matches the current phase better than jumping ahead.</li> </ul> <p>Rank lower when a task:</p> <ul> <li>Depends on unavailable hardware or supervisor input.</li> <li>Is a later-phase feature.</li> <li>Adds polish before a runnable vertical slice exists.</li> <li>Produces code without a clear run-bundle or test artifact.</li> </ul> <h2 id="ready-shelf-rule">Ready/Shelf Rule</h2> <p>A partially built or proposed task is <strong>READY</strong> only when it has:</p> <ul> <li>one authority document or stream-log pointer,</li> <li>bounded files/modules or a bounded artifact target,</li> <li>explicit acceptance evidence or a verification command,</li> <li>no hidden hardware/user/token-budget dependency, and</li> <li>a named lane (<code>[AGENT]</code>, <code>[QUIET-MAC]</code>, or <code>[ED-EXTERNAL]</code>).</li> </ul> <p>If any of those are missing, keep the item as a shelved concept or planning note instead of letting it compete with executable queue work. Half-finished work should be resumed only through its authority pointer and stop-card/checkpoint state, not by inference from prose summaries.</p> <h2 id="machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</h2> <p>Every task carries a lane; a session picks the top task COMPATIBLE with its machine state, not the top task absolutely:</p> <ul> <li><strong>[QUIET-MAC]</strong> — measurement campaigns only: no agent fleet, no Codex load, idle gate will flag contamination.</li> <li><strong>[AGENT]</strong> — code, docs, feasibility spikes; safe during agent-heavy sessions.</li> <li><strong>[ED-EXTERNAL]</strong> — needs the user: advisor, calendar, device access, purchases, destinations.</li> </ul> <h2 id="historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</h2> <p>The former hand-authored live table was removed because it duplicated kernel tasks. Dated completion and disposition history remains below; the generated Current Queue region is the sole live work-selection view.</p> <h2 id="completed-queue-items">Completed Queue Items</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Priority</th> <th>Completed</th> <th>Task</th> <th>Evidence</th> </tr> </thead> <tbody><tr> <td>CODEX-BRIDGE-PET</td> <td>P4 Polish</td> <td>2026-07-18</td> <td>Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing</td> <td>No phase exit-checklist row exists for this personal bridge UI integration; actual <code>scripts/codex-bridge</code> route traced, app-owned thread follower implemented, live Sol/high app-thread smoke <code>019f77a9-2827-7de1-accf-ac2eda21927e</code>, focused IPC/termination tests, and report <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code></td> </tr> <tr> <td>P2-015-SMOKE</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this precondition; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0), pinned in <code>docs/phase_2/detection_floor.md</code>; the extra-sampler overhead layer is deferred with DF-TELEM and remains required before enabling extra samplers</td> </tr> <tr> <td>P2-038</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Close the production-uncertainty live tail with a true MLX + <code>/usr/bin/powermetrics</code> production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this hardening gate; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0); drain fixes PR #72 + PR #74; exact <code>caffeinate -is</code> command and display-sleep environment pin recorded in <code>docs/phase_2/detection_floor.md</code></td> </tr> <tr> <td>AXI-SC</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict <code>unsupported_for_joulewise</code> (external draft: <code>event_observability</code>; native MTP: <code>native_mtp_generation</code>); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #73 merged; lead-run live probes with evidence + SHA-256 (<code>docs/process_traces/2026-07-17-axi-sc-live-probes/</code>); negative applicability verdict filed in <code>docs/specs/axi/sc_spec_decode_verdict.md</code>; vLLM leg remains fixture-first PROVISIONAL and outside this filing</td> </tr> <tr> <td>AXI-SB</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict <code>supported</code> (mlx-lm 0.31.3 BatchGenerator path; true B&gt;1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #70 merged (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); lead-run live probes B∈{2,4} with evidence + SHA-256 (<code>docs/process_traces/2026-07-16-axi-sb-live-probes/</code>); anti-gaming lens -&gt; fix -&gt; delta 2 blockers (9th fix-rounds-inject-defects datum) -&gt; micro-round -&gt; lead termination (post-hardening live re-probe <code>supported</code> at controller_evidence_validation); verdict doc <code>docs/specs/axi/sb_static_batch_verdict.md</code>; ledger <code>docs/stream_logs/2026-07-16-axi-sb.md</code></td> </tr> <tr> <td>SPLIT-AP</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION</td> <td>No matrix row exists in a phase exit checklist for this pre-registration stream; PR #69 merged <code>9db4546</code> (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); Sol xhigh impl -&gt; xhigh counterreview -&gt; fix -&gt; delta (caught lead-pinned predictor blocker) -&gt; micro-round -&gt; focused delta -&gt; bench fix -&gt; MR1 -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-split-ap.md</code> (SPLITAP-1..10)</td> </tr> <tr> <td>SITE-02</td> <td>P4 Polish</td> <td>2026-07-16</td> <td>Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step)</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #68 merged <code>2778ed2</code> (self-merge under Ed&#39;s 2026-07-16 delegation; D2 step verified executed in the release-chain CI log, <code>Ran 1 test ... OK</code>); Sol high impl -&gt; bug+test lenses -&gt; fix -&gt; delta -&gt; micro-round -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-site-02.md</code> (SITE02-1..5)</td> </tr> <tr> <td>AXI-SA</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last)</td> <td>No matrix row exists in a phase exit checklist for this contract stream; spec <code>docs/specs/axi/sa_burst_decode_contract.md</code> is the authority; Sol xhigh impl, xhigh checker FAIL 5 blockers -&gt; fix -&gt; xhigh delta FAIL 2 -&gt; micro-round -&gt; lead termination (canonical 1626 OK, mock spec-decode e2e replayed at the lead bench); PR #67 merged <code>7593259</code> (self-merge under Ed&#39;s 2026-07-16 in-session delegation; CI-only portability fix <code>0914374</code> reviewed fresh, CI green 5/5); run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>AXI-S0</td> <td>P2 Next Slice</td> <td>2026-07-15</td> <td>AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh)</td> <td>No matrix row exists in a phase exit checklist for this docs stream; kernel row completed (AXI-SA dep satisfied); Sol high impl, fresh checker FAIL 4 majors -&gt; fix round -&gt; delta PASS; freshness+suite green; run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>SITE-01</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Site capsule under the 1 MiB Lakebed cap + live redeploy</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #63 (gzip shards, measured-artifact postcondition); delta re-audit no-blockers (D3 fixed, D1/D2 → SITE-02); live deploy ACCEPTED at 854,349 B, routes 5/5 200, freshness 14/14 current; reports <code>2026-07-12-agent-lane-triple.md</code> + <code>2026-07-13-restart-merge-deploy.md</code></td> </tr> <tr> <td>P2-028</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Response-hash determinism gate (<code>joulewise determinism-gate</code>)</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist gate task; PR #62 + DRA-001 malformed-identity fix; both retained corpus groups formally <code>determinism_supported</code>; ledger P2028-1..5; same two reports</td> </tr> <tr> <td>P2-049</td> <td>P3 Hardening Candidates</td> <td>2026-07-13</td> <td>analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3)</td> <td>No matrix row exists in a phase exit checklist for this hardening task; PR #61 (lens CLEAN, replay 1261 OK); installed-wheel CI now smokes the refusal (XSI-1 fix on main); same two reports</td> </tr> <tr> <td>CODEX-BRIDGE-3</td> <td>P0 Safety</td> <td>2026-07-13</td> <td>bridge-protocol/v1.1 for maximum co-work (Ed-directed): discussion lane, session-open/close wrappers, tolerant envelope, per-call reverse effort, peer channels + proposal diffs</td> <td>PR #65 MERGED <code>d285989</code> (Ed-named merge); merged-main suite 1387 OK lead-run; 3 lenses + 3 delta re-audits, findings 13→6→2→1; suite 1387 OK; CI green at <code>8b96bd4</code>; D-065; report <code>2026-07-13-bridge-v11.md</code></td> </tr> <tr> <td>CODEX-BRIDGE-2</td> <td>P0 Safety</td> <td>2026-07-12</td> <td>Make the Claude Code ↔ Sol/Fable bridge bidirectional with adaptive Sol effort (<code>high</code> default; xhigh/ultra only by trigger) and a hard one-hop guard</td> <td>Claude → Sol live <code>/codex</code> token <code>JOULEWISE_SOL_HIGH_GUARDED_OK</code>, thread <code>019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26</code>; Sol → Fable live <code>consult_fable</code> token <code>JOULEWISE_FABLE_MCP_OK</code>, thread <code>019f5a26-d8a6-7993-b48d-8131d88748b9</code>; protocol checker + 4 focused tests; report <code>2026-07-12-claude-sol-bridge.md</code></td> </tr> <tr> <td>INT-59</td> <td>P2 Next Slice</td> <td>2026-07-11</td> <td>Bounded integration-review cleanup/ratio-readiness follow-up</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this integration-review follow-up; PR #59 MERGED 2026-07-11; post-merge main canonical 1,258 OK/10 skipped at <code>194ea39</code> (lead-run)</td> </tr> <tr> <td>DOC-008</td> <td>P2 Next Slice</td> <td>PARTIAL — REOPENED 2026-07-15</td> <td>Machine-readable state kernel (schema v3, <code>AUTHORITATIVE_WORK_SELECTION_STATE</code> for work selection only) generating the RUN_STATE restart block + live queue view</td> <td>PR #60&#39;s 2026-07-11 completion record is reopened by WO-021 because the original spec conditions were only partially satisfied; phase A adds global gates, independent-oracle fidelity checks, CI drift enforcement, and DOC-010&#39;s two-part fence. DOC-008 may not return to complete until every condition in <code>docs/specs/c027/doc-008_state_kernel.md</code> §1.1 lands.</td> </tr> <tr> <td>C-028</td> <td>P0/P1 integration arc</td> <td>2026-07-11</td> <td>Close the #41-#58 hardening + analysis-engine arc; clear the stop card while tracking #59 separately</td> <td><code>docs/run_reports/2026-07-11-c028-continuation.md</code>; council C-028; D-064; main canonical 1,220 OK/10 skipped; corpus 6/6</td> </tr> <tr> <td>C028-SWEEP</td> <td>P4 consistency</td> <td>2026-07-11</td> <td>C-002/D-023 end-of-arc consistency sweep and advisor-doc refresh</td> <td>Same dated C-028 report closeout addendum; <code>claims_lint --mode all</code>; diff/scope checks</td> </tr> <tr> <td>P2-015-PREP</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>P2-015 detection-floor design doc — combined floors, error budget, telemetry trust, and calibration runbooks</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this design-doc task; <code>docs/phase_2/detection_floor.md</code>; D-054; PR #31; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave1.md</code></td> </tr> <tr> <td>P2-029</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Reducer/aggregator uncertainty propagation and claim gates</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-057; PR #33; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-030</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Ordering executability: rotation policies and order provenance</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-056; PR #34; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-031</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Token-normalization contract and stack-identity table</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist contract task; D-058; PR #35; <code>docs/contracts/token_normalization.md</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-032</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign packs: Q1-Q3 split suite, Q6 rail-vs-wall, and C5-2.3 KV economics</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #36; <code>docs/campaign_packs/</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-034</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Broad campaign packs: C5-2.7/2.8, replication runbook, and C5-I.1..I.5</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #39; six packs in <code>docs/campaign_packs/</code>; pack lint errors=0; run report <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code></td> </tr> <tr> <td>CODEX-BRIDGE</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Make the Claude Code → Codex bridge durable, full-session capable, and process-safe</td> <td>Root <code>AGENTS.md</code>; tracked Claude subagent + <code>/codex</code> command; protocol checker; Claude-approved live <code>codex</code> + same-thread <code>codex-reply</code> smoke; report <code>2026-07-09-claude-codex-mcp-bridge.md</code></td> </tr> <tr> <td>RESUME-CP5</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Resume and complete the CP-5 pre-campaign review session</td> <td>7 PRs merged (#22..#28); stop card CLEARED; CP-6 dispositions in the stream log; run report <code>2026-07-09-cp5-resume.md</code>; suite 822 OK</td> </tr> <tr> <td>P2-026</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>D-033 strict legacy-bypass close (frozen six-identity allowlist)</td> <td>PR #22; live-gated 6/6 corpus + tamper-fails + spoof probe fails closed</td> </tr> <tr> <td>P2-025</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign-runner expected-vs-realized prompt-hash check (+ runtime/validator closure)</td> <td>PRs #24 + #27; fail-closed with type-discriminated sidecar inference; live-gated classifier truth table; 48/48 real-tokenizer closures</td> </tr> <tr> <td>P2-010b-GATE</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Envelope-gate analysis script (E1-E4 + E5 advisory, D-036 verdicts, CLI)</td> <td>PR #23; live-gated on the real mock affine bundle incl. refusal cases</td> </tr> <tr> <td>P2-027-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Bundle-pack publication tooling (pack + one-command verify)</td> <td>PR #25; live pack→verify→tamper→verify(2)</td> </tr> <tr> <td>CAPTURE-HARDENING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Pre-campaign capture: output token IDs, fail-closed sampler pin (D-047 amendment), model weight hashing, env versions, hash-domain closure</td> <td>PR #27; live MLX gate incl. two full jw_mixed suite runs</td> </tr> <tr> <td>P2-012-MANIFESTS</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Tokenizer identity widening + real-tokenizer manifest regeneration</td> <td>PR #26; byte-identical double-regen; counts 512/512</td> </tr> <tr> <td>ADVISOR-SITE</td> <td>P4 Polish</td> <td>2026-07-09</td> <td>Advisor status site + suite_next draft-spec packet landing (D-051)</td> <td>PR #28; stop-card sha-verified intact; site regenerated with real renderer</td> </tr> <tr> <td>P2-018</td> <td>P4 Polish</td> <td>2026-07-08</td> <td>Deploy the site as a shareable Lakebed capsule with live GitHub freshness</td> <td>Live at <a href="https://quiet-signal-6af8833395.lakebed.app">https://quiet-signal-6af8833395.lakebed.app</a>; <code>scripts/pack_capsule.py</code> + <code>site_capsule/</code>; per-source drift vs <code>main</code>, fails soft; run report <code>2026-07-08-lakebed-deploy.md</code></td> </tr> <tr> <td>P2-021</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Drift sentinels + block-position covariates in the 2M generator</td> <td>PR #15 (merged 8765ee1); fail-loud sentinel manifest; campaign-log covariate echo; run report <code>2026-07-08-suite-science-expansion.md</code></td> </tr> <tr> <td>P2-017</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Honest per-source site provenance stamps</td> <td>PR #13 site-observatory rewrite: <code>git log -1 -- &lt;source&gt;</code> per page + <code>+ uncommitted</code> dirty marker; parser-tested; run report <code>2026-07-08-site-observatory.md</code></td> </tr> <tr> <td>P2-011</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment)</td> <td>PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace</td> </tr> <tr> <td>P2-008</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Mock telemetry × SystemClock strictly-interior stamping</td> <td>PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired</td> </tr> <tr> <td>P2-009</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Rich telemetry + idle-quality gate + environment capture</td> <td>PR #4 + INT-002 (8856c04); idle gate first live true positive</td> </tr> <tr> <td>2M-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Campaign matrix generator + resumable sequential runner</td> <td>PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified</td> </tr> <tr> <td>KV-SIZE</td> <td>P3 Research Expansion</td> <td>2026-07-07</td> <td>Stage 3.0.0 kv-size helper (module + CLI verb)</td> <td>PR #2; anchors verified against both mirrored models</td> </tr> <tr> <td>FLAGSHIP-001</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max</td> <td>3/3 strict-valid bundles: ~304.0 J gross / ~298.7 J idle-sub per 512-tok request, 582-585 mJ/generated-output-token idle-sub (mean 583.4), 46 tok/s, gross CV 0.3% within one warm-cache session; legacy L1 (bases corrected 2026-07-09, C-027); run report <code>2026-07-07-flagship-qwen35-122b.md</code>; first Q4 data point</td> </tr> <tr> <td>P1-002</td> <td>P1 Phase Gate</td> <td>2026-07-06</td> <td>Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + <code>sudo -n</code> verified, MLX installed</td> <td>Phase 1 exit checklist instrumentation section; fixture committed; live 2I run</td> </tr> <tr> <td>P2-003</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — <strong>first real energy numbers</strong></td> <td>Commits <code>3eb0acd</code>/<code>26dca41</code>/<code>b4d4173</code>; 3/3 strict-valid bundles: ~47.2 J gross / ~44.4 J idle-sub per 512-token request, 79.4-90.5 mJ/generated-output-token idle-sub (mean 86.8), 257 tok/s, TTFT ~94 ms; legacy L1 (bases corrected 2026-07-09, C-027; the old 77-88 figure used the prompt+output denominator); run reports 2026-07-06 (buildout, 2H, 2I)</td> </tr> <tr> <td>P0-002</td> <td>P0 Safety</td> <td>2026-07-06</td> <td>Measurement-corpus backup protocol (R-016) — interim destination per user direction</td> <td><code>scripts/backup_runs.sh</code>; restore test green (<code>validate-bundle</code> on restored copy); protocol in R-016; follow-up P0-003 tracks the real destination</td> </tr> <tr> <td>P3-001</td> <td>P3 Research Expansion</td> <td>2026-07-06</td> <td>Background/related-work draft (Phase 4 Stage 4.6)</td> <td><code>docs/phase_4/related_work_draft.md</code>: 11 sources, independently verified citations, positioning claims honestly adjusted (claims 1-2 narrowed, claim 3 stands)</td> </tr> <tr> <td>2G (P2-003 part)</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>MLX runtime adapter — first real generation traces on the M3 Max</td> <td>Commit <code>3eb0acd</code>; succeeded bundle <code>example-mac-mlx-mock-telemetry</code> (TTFT 81.5 ms, 265.8 tok/s, <code>--strict</code> valid); suite 230 OK both interpreters; implemented by Codex via <code>scripts/codex-bridge</code>, reviewed + live-verified by Claude</td> </tr> <tr> <td>DOC-006</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Independent status-review intake (user-directed): all three findings verified and fixed — P1 event-timestamp hardening, P2 <code>validate-bundle --strict</code> (D-030), P3 adapter raw-write helper</td> <td>Review <code>2026-07-06-project-status-review.md</code>; fixes run report <code>2026-07-06-status-review-fixes.md</code>; 226 tests OK</td> </tr> <tr> <td>P2-007</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Slice 2N pre-hardware hardening (all nine items, three commits)</td> <td>Run report <code>2026-07-06-slice-2n-pre-hardware-hardening.md</code>; D-024..D-029; 216 tests OK; exit-checklist 2N row closed</td> </tr> <tr> <td>DOC-005</td> <td>P4 Polish</td> <td>2026-07-06</td> <td>External architecture review intake (user-directed): D-024 RunContext, D-025 shared bundle reader, node-worker protocol contract, 2N items 8-9</td> <td>Run report <code>2026-07-06-architecture-review-intake.md</code>; <code>docs/contracts/node_worker_protocol.md</code></td> </tr> <tr> <td>DOC-004</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Agent playbook (user-directed): per-mission execution guides for all remaining steps</td> <td><code>docs/agent_playbook.md</code>; pointers in <code>README.md</code>/<code>AGENT_PLAN.md</code>; Stage 4.6 seeded with named competitor set</td> </tr> <tr> <td>P0-001</td> <td>P0 Safety</td> <td>2026-07-05</td> <td>Move repo off iCloud-synced Desktop (R-017)</td> <td>New path <code>~/code/CapstoneRivoire/Capstone</code>; git + suite verified green at the new location; recorded in <code>RUN_STATE.md</code></td> </tr> <tr> <td>DOC-003</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Docs/meta-layer cleanup (user-directed): drift fixes, D-023 status consolidation, plan/guide dedup, R-016/R-017, Slice 2N + Stage 4.6 planned</td> <td>Run report <code>2026-07-05-docs-meta-cleanup.md</code>; D-023; risk register updated</td> </tr> <tr> <td>P2-001</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Mock vertical slice: slices 2A-2E</td> <td>Harness runs end-to-end; <code>validate-bundle</code> green; CI mock e2e step added; 169 tests. <code>joulewise/{bundle,clock,controller,reduce,cli}.py</code> + <code>adapters/</code>; run report <code>2026-06-12-phase-2-mock-vertical-slice.md</code></td> </tr> <tr> <td>P2-002</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Repetitions + experiment manifests (slice 2F)</td> <td><code>run_experiment</code> + cooldown gate; 3-rep + kill-after-rep-2 + cooldown tests; manifest per D-005. Same run report</td> </tr> <tr> <td>P2-J</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Static report generator (slice 2J)</td> <td><code>joulewise/report.py</code>; matplotlib behind <code>[analysis]</code>; graceful structured failure when absent; tests skip cleanly without the extra</td> </tr> <tr> <td>P1-005</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Hailo feasibility verdict</td> <td><code>unsupported_workload</code> from official-source desk research; recorded in the Phase 1 exit checklist Hailo section</td> </tr> <tr> <td>P1-007</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Phase 2 readiness review</td> <td>Recorded in the Phase 1 exit checklist; verdict &quot;mock-first Phase 2 may begin&quot;</td> </tr> <tr> <td>Q-000</td> <td>P0 Safety</td> <td>2026-06-09</td> <td>Resolve the local <code>Energy_Benchmark_Architecture.docx</code> deletion decision</td> <td>User confirmed the Word doc was unrelated; deletion committed in <code>a5d7404</code></td> </tr> <tr> <td>PLAN-001</td> <td>P1 Phase Gate</td> <td>2026-06-09</td> <td>Build evidence-shaped plans for Phases 2-5 (user-directed)</td> <td>Per-phase plan + exit-checklist docs; <code>docs/decision_log.md</code> (D-001..D-019); <code>docs/risk_register.md</code>; <code>docs/milestones.md</code>; methodology/bundle-layout amendments; <code>AGENT_PLAN.md</code> restructured as index; run report <code>docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md</code></td> </tr> <tr> <td>CI-001</td> <td>P2 Next Slice</td> <td>2026-06-09</td> <td>Add core-tests CI workflow (D-017)</td> <td><code>.github/workflows/ci.yml</code>; extended 2026-06-12 with the mock end-to-end run</td> </tr> <tr> <td>DOC-001</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Unify Phase 1 doc scheme with Phases 2-5 (user-directed)</td> <td><code>docs/phase_1/</code> reduced to <code>phase_1_plan.md</code> + <code>phase_1_exit_checklist.md</code>; contracts moved to <code>docs/contracts/</code>; run report <code>docs/run_reports/2026-06-09-phase-1-doc-unification.md</code></td> </tr> <tr> <td>DOC-002</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed)</td> <td>Root <code>PROJECT_STATUS.md</code>; run report <code>docs/run_reports/2026-06-09-advisor-status-doc.md</code></td> </tr> </tbody></table></div> <h2 id="shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</h2> <p>Previously promised follow-ups whose queue rows had silently died; each now has an explicit disposition:</p> <ul> <li><p>D-013 SSH-controlled vs co-resident controller comparison — SHELF, trigger: first 2K live session (validation cell rides that session).</p> </li> <li><p>Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF, trigger: Window-A calibration data exists (P2-015 output feeds it).</p> </li> <li><p><code>dvfm_states</code> slimming option — SHELF, trigger: bundle-size pain during the 2M campaign; otherwise declined as premature.</p> </li> <li><p>Cold-load / model-load-energy capture — DECLINED for the capstone scope (CP-5 deferral made permanent unless an AP row claims it; warm-cache protocol is the declared scope).</p> </li> <li><p>CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).</p> </li> <li><p>DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).</p> </li> </ul> <h2 id="current-do-not-do-yet-list">Current Do-Not-Do-Yet List</h2> <ul> <li>(satisfied 2026-06-12) The mock bundle/reducer path and report generator now exist; dashboard/report work is no longer blocked.</li> <li>(satisfied 2026-06-12) The mock lifecycle is runnable, so live MLX/powermetrics implementation may proceed once its hardware gates open (P1-002 + D-016); follow <code>docs/phase_2/hardware_slice_implementation_guide.md</code>.</li> <li>(resolved 2026-06-12) Hailo feasibility has a verdict (<code>unsupported_workload</code>); do not implement a Hailo backend — report it as an applicability finding.</li> <li>Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in D-008; implementation waits).</li> <li>Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware pairings, or borrow-window scheduling before 2M baselines and the Stage 3.0 verdicts exist (C-007 wording fix; was previously stated as a blanket Phase 3 hold that contradicted the queue).</li> <li>Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the rehearsed runbook exist (R-006).</li> <li>Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has produced data.</li> <li>Do not close D-016 (model selection) without P1-001 supervisor scope or an explicit user go-ahead.</li> <li>(satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own gates (D-016 + <code>[mac]</code> install; privileged sample + D-004 sudoers) open — build on the post-2N seams (RunContext raw evidence, D-026 markers, D-027 rail rows, 2N.3 observed-token fallback).</li> </ul> <h2 id="queue-maintenance">Queue Maintenance</h2> <p>At the end of substantial work:</p> <ul> <li>Update live status, rank, dependencies, and new tasks in <code>docs/process/state_kernel.json</code>.</li> <li>Remove terminal tasks from the kernel only after their owning completion evidence supports closure; preserve the dated Completed row here.</li> <li>Run <code>python3 scripts/gen_state.py</code>; never hand-edit generated queue or restart rows.</li> <li>Keep hand-authored edits here to policy, completed/history records, and non-selection context.</li> </ul> <h2 id="current-queue">Current Queue</h2> <p>The generated region below is the sole live queue and source of truth for work selection. Edit the kernel and regenerate; do not hand-edit its rows.</p> <p>Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see <code>docs/contracts/analysis_plans.md</code> §Required fields.</p> <p>Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see <code>docs/specs/c027/rpt-001_report_vertical_slice.md</code> §0.4 and <code>docs/contracts/publication_privacy.md</code> §Publication boundary.</p> <!-- BEGIN GENERATED: state-kernel current-queue --> <!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. --><p>Source of truth for work selection: <a href="docs/process/state_kernel.json">state kernel</a> (updated 2026-07-25).</p> <p>Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.</p> <div class="table-scroll"><table> <thead> <tr> <th>Rank</th> <th>ID</th> <th>Priority</th> <th>Status</th> <th>Task</th> <th>Evidence / Acceptance</th> </tr> </thead> <tbody><tr> <td>E1</td> <td>P1-008</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</td> <td>Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: <a href="docs/milestones.md">Milestones + R-012</a>. Acceptance: <a href="docs/process/state_kernel.json">P1-008 acceptance</a>. Note: R-012 is the biggest active management risk for an undergrad timeline.</td> </tr> <tr> <td>E2</td> <td>P2-027</td> <td>P2 Next Slice</td> <td>READY [ED-EXTERNAL]</td> <td>Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party.</td> <td>Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-020 + C-027 NEG-9</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-027 acceptance</a>. Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL.</td> </tr> <tr> <td>E3</td> <td>P1-001</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Capture supervisor approval and scope notes.</td> <td>Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: <a href="docs/risk_register.md">R-001</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped.</td> </tr> <tr> <td>E4</td> <td>P1-003</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method.</td> <td>Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: <a href="docs/decision_log.md">D-018/C-003</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Elevated value: gates Q6 boundary sensitivity (C-003).</td> </tr> <tr> <td>E5</td> <td>P1-004</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method.</td> <td>Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: <a href="docs/risk_register.md">R-011</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Partial.</td> </tr> <tr> <td>E6</td> <td>P1-006</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L).</td> <td>Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: <a href="docs/phase_2/hardware_slice_implementation_guide.md">Remote gate / NV-GATE-2</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>.</td> </tr> <tr> <td>Q1</td> <td>P2-015</td> <td>P2 Next Slice</td> <td>PARTIAL; READY [QUIET-MAC]</td> <td>Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</td> <td>Reducer-0.5.2/0.6.2 strict-valid calibration bundles; per-metric floor_abs_j and floor_cmp_j; governed idle uncertainty retained; calibration manifest hash cited by later reports. Evidence: Versioned strict-valid calibration bundles; Per-metric/window-class floor_abs_j + floor_cmp_j; Calibration manifest hash cited by later reports. Authority: <a href="docs/phase_2/detection_floor.md">D-054 + detection floor spec</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Fence: Claim-bearing collection requires fresh 59-pulse protocol-v3 calibration BRACKETING the window (consumed max(B_pre,B_post)); floor artifacts are claim-licensing only from same-custody-session governed extraction until FLOOR-BIND-01 closes (D-078 clause 8 (L1) + bracketing ruling). Note: PR #79 instrument repair and PR #85 SCREEN+BUDGET rules are merged; the start gate is one clean quiet window executed per docs/phase_2/window_runbook.md.</td> </tr> <tr> <td>Q2</td> <td>P2-006</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors measured first) [QUIET-MAC]</td> <td>Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.</td> <td>Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: <a href="docs/phase_2/phase_2_plan.md">Phase 2 plan + analysis plans</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Note: Software interpretation gates are satisfied; execution remains blocked until P2-015 Window-A floors complete.</td> </tr> <tr> <td>Q3</td> <td>P2-010</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (quiet-window tail available after floors) [QUIET-MAC]</td> <td>P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail.</td> <td>joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: <a href="docs/contracts/analysis_plans.md">AP-5 + affine stream log</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-010 acceptance</a>. Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains.</td> </tr> <tr> <td>Q4</td> <td>P2-019</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).</td> <td>Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: <a href="docs/contracts/analysis_plans.md">AP-1</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-019 acceptance</a>.</td> </tr> <tr> <td>Q5</td> <td>P2-020</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts.</td> <td>Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: <a href="docs/contracts/analysis_plans.md">AP-6 + D-046</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-020 acceptance</a>. Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6).</td> </tr> <tr> <td>Q6</td> <td>P2-012</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC]</td> <td>Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases.</td> <td>Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: <a href="docs/contracts/analysis_plans.md">AP-4 + D-039/D-040</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-012 acceptance</a>. Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27).</td> </tr> <tr> <td>Q8</td> <td>P2-046B</td> <td>P1 Phase Gate</td> <td>READY [QUIET-MAC]</td> <td>Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts.</td> <td>Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C6</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-046B acceptance</a>. Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution.</td> </tr> <tr> <td>Q9</td> <td>P2-047B</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist), P2-047A (frozen controller-overhead harness exists) [QUIET-MAC]</td> <td>Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict.</td> <td>Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047B acceptance</a>.</td> </tr> <tr> <td>A0</td> <td>P2-035</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-015 (P2-015 detection floors measured) [AGENT]</td> <td>RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).</td> <td>Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: <a href="docs/specs/rq_energy_variance_design.md">RQ-ENERGY-VARIANCE candidate design</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-035 acceptance</a>. Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine).</td> </tr> <tr> <td>A3</td> <td>FLOOR-BIND-01</td> <td>P1 Phase Gate</td> <td>READY [AGENT]</td> <td>Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</td> <td>Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: <a href="docs/decision_log.md">D-078 clause 8 (confirmation round 9, registered limitation L1)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-BIND-01 acceptance</a>. Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed.</td> </tr> <tr> <td>A4</td> <td>AXI-SB-ADAPTER</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.</td> <td>The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: <a href="docs/specs/axi/sb_static_batch_verdict.md">AXI-SB verdict document (supported; mint-on-supported follow-on)</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SB-ADAPTER acceptance</a>. Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A6</td> <td>AXI-SD</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Prepare the matched dense/MoE pair proposal with the consult&#39;s pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT.</td> <td>A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016&#39;s cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-D</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SD acceptance</a>. Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A7</td> <td>AXI-SE</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (P2-015 publishes Window-A floors before AXI analysis plans are finalized) [AGENT]</td> <td>Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult&#39;s floor and ownership closures.</td> <td>The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A&#39;s gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-E</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SE acceptance</a>. Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership).</td> </tr> <tr> <td>A16</td> <td>P3-000</td> <td>P3 Research Expansion</td> <td>BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT]</td> <td>KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8).</td> <td>Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: <a href="docs/decision_log.md">D-035/D-036</a>. Acceptance: <a href="docs/phase_3/phase_3_exit_checklist.md">Phase 3 exit checklist</a>. Note: 3.0.1 complete and merged (PR #9, replay_supported).</td> </tr> <tr> <td>A17</td> <td>P2-022</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT]</td> <td>Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported).</td> <td>3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/contracts/adapter_contracts.md">Adapter contract</a>. Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission.</td> </tr> <tr> <td>A18</td> <td>P2-023</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT]</td> <td>HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy.</td> <td>Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/research_question_bank.md">RQ bank import-smoke design</a>. Fence: No pass@k, accuracy, or capability claim (D-041).</td> </tr> <tr> <td>A19</td> <td>P2-024</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (2M reductions identify floor/MDE headroom), P2-015 (Window-A floors measured) [AGENT]</td> <td>Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC].</td> <td>Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: <a href="docs/research_question_bank.md">C-015 + RQ bank</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-024 acceptance</a>.</td> </tr> <tr> <td>A21</td> <td>P3-001b</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-006 (2M affine coefficients exist) [AGENT]</td> <td>Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049).</td> <td>AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: <a href="docs/decision_log.md">D-048/D-049</a>. Acceptance: <a href="docs/contracts/analysis_plans.md">Analysis plans (split row)</a>.</td> </tr> <tr> <td>A22</td> <td>P2-004</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES close: P1-001 [AGENT]</td> <td>Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding.</td> <td>Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: <a href="docs/decision_log.md">D-016</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Provisional small-model pick 2026-07-06 opens 2G.</td> </tr> <tr> <td>A23</td> <td>P2-005</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES live_promotion: P1-006 [AGENT]</td> <td>Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute.</td> <td>Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: <a href="docs/specs/c027/nv-gate-2_live_promotion.md">NV-GATE-2 live-promotion spec</a>. Acceptance: <a href="docs/phase_1/2k_live_verification_checklist.md">2K live verification checklist</a>. Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open.</td> </tr> <tr> <td>A24</td> <td>P2-016</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists) [AGENT]</td> <td>Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.</td> <td>Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-011 ledger + C-027 (post-2M umbrella)</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-016 acceptance</a>. Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.</td> </tr> <tr> <td>A25</td> <td>P2-047A</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist before overhead design is frozen) [AGENT]</td> <td>Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes.</td> <td>A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047A acceptance</a>. Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7).</td> </tr> <tr> <td>A29</td> <td>DOC-008-REFLECTION</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6.</td> <td>Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence).</td> </tr> <tr> <td>A30</td> <td>DOC-008-STATUS</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8.</td> <td>Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence).</td> </tr> <tr> <td>A31</td> <td>DOC-008-INTAKE</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9.</td> <td>Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake and procedure reconciliation</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake reconciliation</a>. Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence).</td> </tr> <tr> <td>A32</td> <td>DOC-008</td> <td>P4 Polish</td> <td>PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT]</td> <td>Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked.</td> <td>Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 state-kernel specification</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 required outcomes</a>. Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live.</td> </tr> <tr> <td>A33</td> <td>P2-050</td> <td>P3 Hardening Candidates</td> <td>READY [AGENT]</td> <td>Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2.</td> <td>Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives i </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>TASK_QUEUE.md · commit de665ea · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/site/index.html:17:</header> <main> <section class="readme-hero"> <div class="kicker">Project README · undergraduate capstone · local LLM energy</div> <p class="readme-eyebrow">JouleWise is an extensible measurement harness.</p> <h1>Measure first.<br>Make claims second.</h1> <p class="lede">JouleWise runs language-model inference on local hardware, records power and runtime events together, and seals the evidence into a bundle that can be checked after the machine has gone quiet. The goal is not a prettier leaderboard. It is a defensible way to ask where the joules went.</p> <div class="readme-actions"> <a class="readme-primary" href="research.html">Learn the project top to bottom</a> <a href="status.html">See the live project state</a> <a href="readme.html">Open the repository README</a> </div> <div class="provenance-plate"><span class="source-chip" title="README.md · commit 1af9f92"><span class="source-file">README.md</span><span class="source-commit">commit 1af9f92</span></span> <span class="source-chip" title="docs/decision_log.md · commit 1af9f92 + uncommitted"><span class="source-file">docs/<wbr>decision_log.md</span><span class="source-commit">commit 1af9f92 + uncommitted</span></span> <span class="source-chip" title="docs/site_src/index.html · commit 632d9eb"><span class="source-file">docs/<wbr>site_src/<wbr>index.html</span><span class="source-commit">commit 632d9eb</span></span></div> </section> <section class="band tight readme-section" id="what"> <div class="kicker">What it is</div> <h2>Instrument first, benchmark second.</h2> <div class="readme-definition-grid"> <article class="panel corner"> <div class="card-label">Harness · the instrument</div> <h3>Runs, observes, and preserves.</h3> <p>Typed experiment configs, runtime adapters, telemetry adapters, bundle writing, reduction, and strict validation form the reusable measurement harness. New hardware and runtimes plug into these seams.</p> </article> <article class="panel"> <div class="card-label">Benchmark · a governed use of it</div> <h3>Freezes workloads and rules.</h3> <p>A benchmark is the frozen workload suite, run rules, and strict validator layered on the harness. Calling the whole repository a benchmark would hide the distinction that makes its evidence reusable.</p> </article> </div> <p class="readme-note">This terminology is binding reader-facing policy under D-069. The harness can exist before a benchmark campaign is ready to support a comparison.</p> </section> <section class="band readme-section" id="why"> <div class="kicker">Why it exists</div> <h2>Energy numbers are easy to print and hard to mean.</h2> <div class="readme-problem-grid"> <article><span class="mono">boundary</span><h3>What did you measure?</h3><p>Chip rails, package power, and wall power answer different questions. JouleWise names the boundary beside the result.</p></article> <article><span class="mono">time</span><h3>When did measurement begin?</h3><p>Model loading, sampler startup, prefill, decode, and cooldown must not drift into one another unnoticed.</p></article> <article><span class="mono">noise</span><h3>Could the instrument resolve it?</h3><p>A small difference may be below the detection floor. “Not resolvable” is not the same claim as “no difference.”</p></article> <article><span class="mono">evidence</span><h3>Can someone check it?</h3><p>A summary without its trace, events, configuration, and provenance is an assertion. A strict-valid bundle is an audit trail.</p></article> </div> </section> <section class="band readme-section" id="how"> <div class="kicker">How it works</div> <h2>One path from intent to evidence.</h2> <ol class="readme-flow"> <li><span>config</span><div><h3>Describe the run.</h3><p>Model, workload shape, runtime, telemetry backend, repetitions, and evidence rules begin as typed inputs rather than shell-history folklore.</p></div></li> <li><span>adapters</span><div><h3>Exercise the target.</h3><p>The controller pairs a runtime adapter with a telemetry adapter while recording lifecycle, phase, and token events.</p></div></li> <li><span>bundle</span><div><h3>Keep the raw record.</h3><p>The normalized config, metadata, event log, raw telemetry, outputs, logs, and reduced metrics live together as immutable evidence.</p></div></li> <li><span>strict</span><div><h3>Re-derive, do not merely inspect.</h3><p>Strict validation parses the raw evidence again, recomputes metrics, checks provenance and completion, and fails closed on contradictions.</p></div></li> <li><span>claim</span><div><h3>Ask what the evidence allows.</h3><p>Detection floors, uncertainty, analysis plans, and the claims ladder decide whether a number is descriptive, comparative, or not yet claim-bearing.</p></div></li> </ol> </section> <section class="band readme-section" id="state"> <div class="kicker">Current state</div> <h2>A research prototype with a real evidence path—and unfinished claim gates.</h2> <div class="readme-state-grid"> <article class="panel"> <div class="card-label">Working now</div> <p>The Mac path runs MLX inference with <code>powermetrics</code> telemetry, creates strict-valid bundles, and re-derives results from preserved evidence. The analysis and claim-gating machinery is implemented.</p> </article> <article class="panel"> <div class="card-label">Newest evidence</div> <p>The Window-A floor collection is complete and independently verified. It produced usable floor estimates, but every contributing bundle carries claim-evidence flags. The numbers are calibration evidence, not permission to overstate a model comparison.</p> <div class="provenance-plate"><span class="source-chip" title="docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895"><span class="source-file">docs/<wbr>process_traces/<wbr>2026-07-17-floor-extraction/<wbr>extraction-verified.json</span><span class="source-commit">commit b28c895</span></span></div> </article> <article class="panel"> <div class="card-label">Still gated</div> <p>Comparative campaigns, remote hardware claims, and broad rankings wait on their named floor, evidence, hardware, and analysis gates. The status and roadmap pages read those gates from repository sources.</p> </article> </div> <div class="readme-actions"> <a href="status.html">Current status</a> <a href="roadmap.html">What happens next</a> <a href="library.html">Contracts and source documents</a> </div> </section> <section class="band readme-section readme-measurements-last" id="measurements"> <div class="kicker">Measurements · deliberately last</div> <h2>Read the instrument before reading its numbers.</h2> <p class="lede">Every energy value in the measurement section names its basis and boundary. Gross energy is the headline basis for comparisons; idle-subtracted energy appears only as a labeled within-device secondary view. The page also separates strict-valid collection from claim readiness.</p> <a class="measurement-cta" href="results.html">Open measurements and floor results →</a> </section> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/site_src/index.html · commit 632d9eb · README.md · commit 1af9f92 · docs/decision_log.md · commit 1af9f92 + uncommitted · docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json · commit b28c895 · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/site/adapter_contracts.html:37:</code></pre> <p>Shim events ride the existing run-bundle event shape: the only top-level event keys are <code>timestamp_s</code>, <code>event_type</code>, <code>phase</code>, <code>message</code>, and <code>metadata</code>. Harness-specific data, benchmark item IDs, prompt/output hashes, external metric IDs, status, errors, and any token counts reported by the harness stay inside <code>metadata</code> (C-015).</p> <p>Validation rules for C-015/P2-022: item markers must pair; timestamps must be monotonic; all item markers must fall inside the measured window; item windows must not overlap unless the shim declares an overlapping execution mode; the external result artifact must be preserved and hashed; and strict bundle validation plus reduction must succeed before any energy result is claim-bearing.</p> <p>Permitted claim shapes (C-015):</p> <ul> <li>&quot;External harness X version Y reported metric artifact Z; JouleWise measured energy for the same marked item/subset windows.&quot;</li> <li>L1 observed energy for an external harness run under a named stack, measurement boundary, subset, and output policy.</li> <li>L2 energy comparisons only with strict bundles, repeated runs, same boundary or calibrated boundary, and AP coverage.</li> </ul> <p>Forbidden claims (C-015/C-004):</p> <ul> <li>JouleWise-computed accuracy unless a future quarantined scorer explicitly exists.</li> <li>Intelligence per joule, pass@k per joule, or &quot;more capable per watt.&quot;</li> <li>Leaderboard standing from joined accuracy(theirs)+energy(ours).</li> <li>Item-window statistical independence.</li> <li>Any pass@k, retry, judge, or benchmark-score normalization claim from the shim layer.</li> </ul> <p>The P2-022 feasibility spike launches the external runner as a subprocess and inherits D-035 fresh-process isolation. Its verdict is computed, not hand-labeled, per D-036, from marker pairing, timestamp placement, subprocess exit status, external result hash presence, strict bundle validity, and reduction success. Verdict codes are <code>external_markers_supported</code>, <code>partial(&lt;limitation&gt;)</code>, and <code>external_markers_unsupported</code>.</p> <h2 id="transport-adapter">Transport Adapter</h2> <p>Transport answers where commands execute.</p> <p>Required behavior:</p> <ul> <li>Run a command locally or over SSH.</li> <li>Copy artifacts into the controller&#39;s run bundle.</li> <li>Report connection metadata.</li> <li>Return structured failure on unreachable hosts.</li> </ul> <p>Initial transports:</p> <ul> <li><code>local</code></li> <li><code>ssh</code></li> </ul> <h2 id="runtime-adapter">Runtime Adapter</h2> <p>Runtime answers how a model workload is executed.</p> <p>Required behavior:</p> <ul> <li>Prepare runtime environment.</li> <li>Load or initialize model.</li> <li>Warm up workload.</li> <li>Run full request.</li> <li>Run prefill-only workload when supported (Phase-3-future: no shipped RuntimeAdapter implements or is required to implement this yet; binding form lands with Phase 3 Stage 3.1/3.2 schema v0.2).</li> <li>Run decode-only or replay workload when supported (Phase-3-future: same gating as prefill-only; the contract does not promise split modes the current adapters cannot express).</li> <li>Emit phase events.</li> <li>Emit output artifacts.</li> <li>Cleanup.</li> </ul> <p>Initial runtimes:</p> <ul> <li><code>mock</code></li> <li><code>mlx</code></li> <li><code>vllm</code></li> </ul> <p>Candidate runtimes:</p> <ul> <li><code>llama_cpp</code></li> <li><code>hailo</code></li> </ul> <h2 id="suite-runtime-adapter-d-045-d-046-d-047-5">Suite Runtime Adapter (D-045/D-046/D-047.5)</h2> <p>A runtime that can execute a materialized suite manifest implements <code>SuiteRuntimeAdapter.run_suite(config, manifest, context, *, order_seed, order_row=None)</code>. The controller dispatches to this method only when <code>workload_profile.suite_manifest_ref</code> is set and validation has loaded the manifest. <code>run_workload</code> remains the single-prompt contract. <code>order_seed</code> is controller-derived (D-045.6), never runtime-chosen; adapters must use the supplied value in suite markers and workload provenance rather than deriving a seed from <code>run_id</code>.</p> <p>2026-07-09 (P2-030): <code>order_row</code> is the controller-derived companion to <code>order_seed</code> for operational suite order policies. It is <code>0</code> for single runs and the one-based <code>__rN</code> repetition index for experiment members. Runtimes execute the pure realized order defined by <code>joulewise.suite.realized_order</code> from the manifest policy and <code>order_row</code>; they do not choose or randomize the row.</p> <p><code>run_suite</code> obligations:</p> <ul> <li>Iterate the realized suite order and emit suite, block, level, and item markers with the vocabulary and required metadata keys pinned in <code>joulewise/suite.py</code>. For <code>manifest_order</code> the realized order is manifest order. For rotated policies, <code>item_index</code> remains the manifest index, <code>position</code> is the realized execution ordinal, and <code>prev_item</code> is execution honest.</li> <li>Contain per-item generation exceptions: the item receives <code>item_end</code> with <code>status: &quot;runtime_failed&quot;</code> and a diagnostic <code>status_reason</code>, then the loop continues. Suite-level machinery failures may still raise out of <code>run_suite</code>.</li> <li>Write exactly one per-item output artifact, <code>outputs/suite_items.jsonl</code>. Each line carries the item id/index, status and optional status reason, <code>prompt_source</code>, <code>bos_present</code>, prompt token-ID hash block, response text/hash, stop reason, prompt/output token counts, and token timestamps (D-045.8/AP-6). Suites do not emit <code>response.txt</code>.</li> <li>Preserve workload provenance for suite identity, generator, tokenizer, model, and sampler. MLX adapters must pin greedy/temp-0 by constructing the installed <code>mlx_lm</code> sampler and passing it to <code>stream_generate</code>; if the sampler cannot be constructed or verified, measured single-prompt and suite generation fail closed with the named adapter error <code>sampler_pin_unverified</code>.</li> </ul> <p>Runtime status assignment:</p> <pre><code class="language-text">condition                                           item_end.status
docs/stream_logs/2026-07-16-advisor-refresh.md:32:idle-subtracted energy label with its M3 Max / powermetrics SoC-rails boundary;
docs/site/task_queue.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Task Queue - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#intake-rule-for-new-tasks">Intake Rule For New Tasks</a> <a href="#priority-scale">Priority Scale</a> <a href="#ranking-factors">Ranking Factors</a> <a href="#ready-shelf-rule">Ready/Shelf Rule</a> <a href="#machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</a> <a href="#historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</a> <a href="#completed-queue-items">Completed Queue Items</a> <a href="#shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</a> <a href="#current-do-not-do-yet-list">Current Do-Not-Do-Yet List</a> <a href="#queue-maintenance">Queue Maintenance</a> <a href="#current-queue">Current Queue</a> <a href="#active-global-work-selection-gates">Active Global Work-Selection Gates</a></aside> <div class="doc-wrap doc-source-task-queue-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>TASK_QUEUE.md</code></p> <div class="provenance-plate"><span class="source-chip" title="TASK_QUEUE.md · commit de665ea"><span class="source-file">TASK_QUEUE.md</span><span class="source-commit">commit de665ea</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>JouleWise Task Queue</h1> <p>This is the live queue for JouleWise work. When the user gives a new task, first triage it here instead of assuming it should happen immediately.</p> <h2 id="intake-rule-for-new-tasks">Intake Rule For New Tasks</h2> <p>For every new user task:</p> <ol> <li>Read <code>RUN_STATE.md</code>.</li> <li>Read this file.</li> <li>Check <code>git status --short --branch</code>.</li> <li>Review the last 2-3 commits with <code>git log --oneline --decorate -3</code>.</li> <li>Check relevant handoffs in <code>docs/run_reports/</code>.</li> <li>If <code>RUN_STATE.md</code> contains an ACTIVE <code>ACTIVE_STOP_CARD</code>, that card outranks this queue. Execute or preserve the card&#39;s resume/cleanup instructions before considering any lower-ranked work.</li> <li>Decide whether the task is:<ul> <li>urgent workspace hygiene,</li> <li>Phase 1 evidence work,</li> <li>Phase 2 implementation prep,</li> <li>later-phase research work,</li> <li>documentation/reporting,</li> <li>or unrelated/new scope.</li> </ul> </li> <li>Place or update the task in the queue with priority, rationale, evidence, and blockers.</li> <li>If executing it now, say why it outranks the current top task.</li> <li>Closure rule (D-023): a row may move to Completed only after the corresponding phase exit-checklist matrix row already shows the same status with dated evidence, and the Completed row&#39;s evidence cell must cite that matrix row (file + item id). If no matrix row exists for the work, say so explicitly in the evidence cell.</li> </ol> <h2 id="priority-scale">Priority Scale</h2> <ul> <li><strong>P0 Safety</strong>: prevents accidental data loss, bad commits, broken handoffs, or corrupted repo state.</li> <li><strong>P1 Phase Gate</strong>: required to close the current phase or unblock the next phase responsibly.</li> <li><strong>P2 Next Slice</strong>: next implementation slice after current phase gates are adequately planned or closed.</li> <li><strong>P3 Research Expansion</strong>: useful experiment or feature, but not needed for current gate.</li> <li><strong>P4 Polish</strong>: quality-of-life, dashboard polish, formatting, cleanup, or presentation work.</li> </ul> <h2 id="ranking-factors">Ranking Factors</h2> <p>Rank higher when a task:</p> <ul> <li>Prevents accidental loss or bad Git history.</li> <li>Produces evidence for the current phase exit checklist.</li> <li>Removes ambiguity for multiple later steps.</li> <li>Is required before physical hardware time is spent.</li> <li>Is cheap to verify and reduces future confusion.</li> <li>Matches the current phase better than jumping ahead.</li> </ul> <p>Rank lower when a task:</p> <ul> <li>Depends on unavailable hardware or supervisor input.</li> <li>Is a later-phase feature.</li> <li>Adds polish before a runnable vertical slice exists.</li> <li>Produces code without a clear run-bundle or test artifact.</li> </ul> <h2 id="ready-shelf-rule">Ready/Shelf Rule</h2> <p>A partially built or proposed task is <strong>READY</strong> only when it has:</p> <ul> <li>one authority document or stream-log pointer,</li> <li>bounded files/modules or a bounded artifact target,</li> <li>explicit acceptance evidence or a verification command,</li> <li>no hidden hardware/user/token-budget dependency, and</li> <li>a named lane (<code>[AGENT]</code>, <code>[QUIET-MAC]</code>, or <code>[ED-EXTERNAL]</code>).</li> </ul> <p>If any of those are missing, keep the item as a shelved concept or planning note instead of letting it compete with executable queue work. Half-finished work should be resumed only through its authority pointer and stop-card/checkpoint state, not by inference from prose summaries.</p> <h2 id="machine-state-lanes-adopted-c-007-2026-07-07">Machine-State Lanes (adopted C-007, 2026-07-07)</h2> <p>Every task carries a lane; a session picks the top task COMPATIBLE with its machine state, not the top task absolutely:</p> <ul> <li><strong>[QUIET-MAC]</strong> — measurement campaigns only: no agent fleet, no Codex load, idle gate will flag contamination.</li> <li><strong>[AGENT]</strong> — code, docs, feasibility spikes; safe during agent-heavy sessions.</li> <li><strong>[ED-EXTERNAL]</strong> — needs the user: advisor, calendar, device access, purchases, destinations.</li> </ul> <h2 id="historical-queue-snapshot-superseded-2026-07-15">Historical Queue Snapshot (superseded 2026-07-15)</h2> <p>The former hand-authored live table was removed because it duplicated kernel tasks. Dated completion and disposition history remains below; the generated Current Queue region is the sole live work-selection view.</p> <h2 id="completed-queue-items">Completed Queue Items</h2> <div class="table-scroll"><table> <thead> <tr> <th>ID</th> <th>Priority</th> <th>Completed</th> <th>Task</th> <th>Evidence</th> </tr> </thead> <tbody><tr> <td>CODEX-BRIDGE-PET</td> <td>P4 Polish</td> <td>2026-07-18</td> <td>Make the native Codex pet reflect Claude Code background Sol work without changing adaptive effort routing</td> <td>No phase exit-checklist row exists for this personal bridge UI integration; actual <code>scripts/codex-bridge</code> route traced, app-owned thread follower implemented, live Sol/high app-thread smoke <code>019f77a9-2827-7de1-accf-ac2eda21927e</code>, focused IPC/termination tests, and report <code>docs/run_reports/2026-07-18-claude-codex-pet-observer.md</code></td> </tr> <tr> <td>P2-015-SMOKE</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Complete the pre-Window-A production-shaped campaign shakedown through doctor, strict validation, reducer 0.4.2, strict revalidation, campaign verdict split, and approved backup; keep extra samplers disabled pending DF-TELEM</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this precondition; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0), pinned in <code>docs/phase_2/detection_floor.md</code>; the extra-sampler overhead layer is deferred with DF-TELEM and remains required before enabling extra samplers</td> </tr> <tr> <td>P2-038</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>Close the production-uncertainty live tail with a true MLX + <code>/usr/bin/powermetrics</code> production-shaped shakedown through strict validation, reducer 0.4.2, strict revalidation, request-eligibility gating, and approved backup</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this hardening gate; <code>production_uncertainty_v1</code> PASSED on merged main at <code>runs/window_a_shakedown_final</code> (<code>request_eligible: true</code>, reasons <code>[]</code>, strict pre+post reduce passed, backup exit 0); drain fixes PR #72 + PR #74; exact <code>caffeinate -is</code> command and display-sleep environment pin recorded in <code>docs/phase_2/detection_floor.md</code></td> </tr> <tr> <td>AXI-SC</td> <td>P2 Next Slice</td> <td>2026-07-17</td> <td>AXI stream S-C leg 1: pinned mlx-lm speculative-decode/MTP feasibility spike — verdict <code>unsupported_for_joulewise</code> (external draft: <code>event_observability</code>; native MTP: <code>native_mtp_generation</code>); Mac energy leg not minted, with explicit runtime-upgrade revisit triggers</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #73 merged; lead-run live probes with evidence + SHA-256 (<code>docs/process_traces/2026-07-17-axi-sc-live-probes/</code>); negative applicability verdict filed in <code>docs/specs/axi/sc_spec_decode_verdict.md</code>; vLLM leg remains fixture-first PROVISIONAL and outside this filing</td> </tr> <tr> <td>AXI-SB</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-B: pinned mlx-lm static-batch feasibility spike — verdict <code>supported</code> (mlx-lm 0.31.3 BatchGenerator path; true B&gt;1 execution with full per-request observability); Mac C5-2.2 leg minted per D-070; follow-on adapter row AXI-SB-ADAPTER minted at rank 4</td> <td>No matrix row exists in a phase exit checklist for this spike; PR #70 merged (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); lead-run live probes B∈{2,4} with evidence + SHA-256 (<code>docs/process_traces/2026-07-16-axi-sb-live-probes/</code>); anti-gaming lens -&gt; fix -&gt; delta 2 blockers (9th fix-rounds-inject-defects datum) -&gt; micro-round -&gt; lead termination (post-hardening live re-probe <code>supported</code> at controller_evidence_validation); verdict doc <code>docs/specs/axi/sb_static_batch_verdict.md</code>; ledger <code>docs/stream_logs/2026-07-16-axi-sb.md</code></td> </tr> <tr> <td>SPLIT-AP</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>Split pre-registration freeze (adjudicated Part I, D-067-reconciled): gross-only primary estimand and headline; both monolithic references mandatory (Holm, intersection-union); pinned idle-sub calculation with D-067 reporting restriction; D-048 predictor over all five gross components; named open gates OPEN-GATE-SPLITAP-PACK-LINT + OPEN-SPLIT-PRED-FIXED-COMPOSITION</td> <td>No matrix row exists in a phase exit checklist for this pre-registration stream; PR #69 merged <code>9db4546</code> (self-merge under Ed&#39;s 2026-07-16 delegation; CI green); Sol xhigh impl -&gt; xhigh counterreview -&gt; fix -&gt; delta (caught lead-pinned predictor blocker) -&gt; micro-round -&gt; focused delta -&gt; bench fix -&gt; MR1 -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-split-ap.md</code> (SPLITAP-1..10)</td> </tr> <tr> <td>SITE-02</td> <td>P4 Polish</td> <td>2026-07-16</td> <td>Close SITE-01 D1/D2 deferrals: loud structured Lakebed discovery (env + OS-path, exact-version refusal incl. wrong-before-correct PATH ordering, never silent estimator fallback) + node decode regression executing the EMITTED TypeScript via pinned esbuild; D2 guaranteed in CI (release-chain focused step)</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #68 merged <code>2778ed2</code> (self-merge under Ed&#39;s 2026-07-16 delegation; D2 step verified executed in the release-chain CI log, <code>Ran 1 test ... OK</code>); Sol high impl -&gt; bug+test lenses -&gt; fix -&gt; delta -&gt; micro-round -&gt; lead termination; ledger <code>docs/stream_logs/2026-07-16-site-02.md</code> (SITE02-1..5)</td> </tr> <tr> <td>AXI-SA</td> <td>P2 Next Slice</td> <td>2026-07-16</td> <td>AXI stream S-A: burst-decode metric-semantics contract implementation, stages 0-7 (versioned request-scoped emission events, proposal/acceptance counters, speculation identity, sibling analysis manifest with frozen AP-SPEC denominators, output-identity gate, mock spec adapter last)</td> <td>No matrix row exists in a phase exit checklist for this contract stream; spec <code>docs/specs/axi/sa_burst_decode_contract.md</code> is the authority; Sol xhigh impl, xhigh checker FAIL 5 blockers -&gt; fix -&gt; xhigh delta FAIL 2 -&gt; micro-round -&gt; lead termination (canonical 1626 OK, mock spec-decode e2e replayed at the lead bench); PR #67 merged <code>7593259</code> (self-merge under Ed&#39;s 2026-07-16 in-session delegation; CI-only portability fix <code>0914374</code> reviewed fresh, CI green 5/5); run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>AXI-S0</td> <td>P2 Next Slice</td> <td>2026-07-15</td> <td>AXI stream S-0: advisor-facing doc alignment (gross basis+boundary on every number, D-067 attributed rationale, harness/benchmark split, five-axis Q4 agenda, C-023-IDLE-STATIONARITY note, DRIFT.md refresh)</td> <td>No matrix row exists in a phase exit checklist for this docs stream; kernel row completed (AXI-SA dep satisfied); Sol high impl, fresh checker FAIL 4 majors -&gt; fix round -&gt; delta PASS; freshness+suite green; run report <code>docs/run_reports/2026-07-14-audit-resume-axi.md</code></td> </tr> <tr> <td>SITE-01</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Site capsule under the 1 MiB Lakebed cap + live redeploy</td> <td>No matrix row exists in a phase exit checklist for this site-tooling task; PR #63 (gzip shards, measured-artifact postcondition); delta re-audit no-blockers (D3 fixed, D1/D2 → SITE-02); live deploy ACCEPTED at 854,349 B, routes 5/5 200, freshness 14/14 current; reports <code>2026-07-12-agent-lane-triple.md</code> + <code>2026-07-13-restart-merge-deploy.md</code></td> </tr> <tr> <td>P2-028</td> <td>P2 Next Slice</td> <td>2026-07-13</td> <td>Response-hash determinism gate (<code>joulewise determinism-gate</code>)</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist gate task; PR #62 + DRA-001 malformed-identity fix; both retained corpus groups formally <code>determinism_supported</code>; ledger P2028-1..5; same two reports</td> </tr> <tr> <td>P2-049</td> <td>P3 Hardening Candidates</td> <td>2026-07-13</td> <td>analysis_manifest.py explicit-root-or-fail-closed resolution (C-028 SF3)</td> <td>No matrix row exists in a phase exit checklist for this hardening task; PR #61 (lens CLEAN, replay 1261 OK); installed-wheel CI now smokes the refusal (XSI-1 fix on main); same two reports</td> </tr> <tr> <td>CODEX-BRIDGE-3</td> <td>P0 Safety</td> <td>2026-07-13</td> <td>bridge-protocol/v1.1 for maximum co-work (Ed-directed): discussion lane, session-open/close wrappers, tolerant envelope, per-call reverse effort, peer channels + proposal diffs</td> <td>PR #65 MERGED <code>d285989</code> (Ed-named merge); merged-main suite 1387 OK lead-run; 3 lenses + 3 delta re-audits, findings 13→6→2→1; suite 1387 OK; CI green at <code>8b96bd4</code>; D-065; report <code>2026-07-13-bridge-v11.md</code></td> </tr> <tr> <td>CODEX-BRIDGE-2</td> <td>P0 Safety</td> <td>2026-07-12</td> <td>Make the Claude Code ↔ Sol/Fable bridge bidirectional with adaptive Sol effort (<code>high</code> default; xhigh/ultra only by trigger) and a hard one-hop guard</td> <td>Claude → Sol live <code>/codex</code> token <code>JOULEWISE_SOL_HIGH_GUARDED_OK</code>, thread <code>019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26</code>; Sol → Fable live <code>consult_fable</code> token <code>JOULEWISE_FABLE_MCP_OK</code>, thread <code>019f5a26-d8a6-7993-b48d-8131d88748b9</code>; protocol checker + 4 focused tests; report <code>2026-07-12-claude-sol-bridge.md</code></td> </tr> <tr> <td>INT-59</td> <td>P2 Next Slice</td> <td>2026-07-11</td> <td>Bounded integration-review cleanup/ratio-readiness follow-up</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this integration-review follow-up; PR #59 MERGED 2026-07-11; post-merge main canonical 1,258 OK/10 skipped at <code>194ea39</code> (lead-run)</td> </tr> <tr> <td>DOC-008</td> <td>P2 Next Slice</td> <td>PARTIAL — REOPENED 2026-07-15</td> <td>Machine-readable state kernel (schema v3, <code>AUTHORITATIVE_WORK_SELECTION_STATE</code> for work selection only) generating the RUN_STATE restart block + live queue view</td> <td>PR #60&#39;s 2026-07-11 completion record is reopened by WO-021 because the original spec conditions were only partially satisfied; phase A adds global gates, independent-oracle fidelity checks, CI drift enforcement, and DOC-010&#39;s two-part fence. DOC-008 may not return to complete until every condition in <code>docs/specs/c027/doc-008_state_kernel.md</code> §1.1 lands.</td> </tr> <tr> <td>C-028</td> <td>P0/P1 integration arc</td> <td>2026-07-11</td> <td>Close the #41-#58 hardening + analysis-engine arc; clear the stop card while tracking #59 separately</td> <td><code>docs/run_reports/2026-07-11-c028-continuation.md</code>; council C-028; D-064; main canonical 1,220 OK/10 skipped; corpus 6/6</td> </tr> <tr> <td>C028-SWEEP</td> <td>P4 consistency</td> <td>2026-07-11</td> <td>C-002/D-023 end-of-arc consistency sweep and advisor-doc refresh</td> <td>Same dated C-028 report closeout addendum; <code>claims_lint --mode all</code>; diff/scope checks</td> </tr> <tr> <td>P2-015-PREP</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>P2-015 detection-floor design doc — combined floors, error budget, telemetry trust, and calibration runbooks</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this design-doc task; <code>docs/phase_2/detection_floor.md</code>; D-054; PR #31; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave1.md</code></td> </tr> <tr> <td>P2-029</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Reducer/aggregator uncertainty propagation and claim gates</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-057; PR #33; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-030</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Ordering executability: rotation policies and order provenance</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist implementation task; D-056; PR #34; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-031</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Token-normalization contract and stack-identity table</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this post-checklist contract task; D-058; PR #35; <code>docs/contracts/token_normalization.md</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-032</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign packs: Q1-Q3 split suite, Q6 rail-vs-wall, and C5-2.3 KV economics</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #36; <code>docs/campaign_packs/</code>; run report <code>docs/run_reports/2026-07-09-spec-fleshing-wave2.md</code></td> </tr> <tr> <td>P2-034</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Broad campaign packs: C5-2.7/2.8, replication runbook, and C5-I.1..I.5</td> <td>No matrix row exists in <code>docs/phase_2/phase_2_exit_checklist.md</code> for this campaign-pack task; PR #39; six packs in <code>docs/campaign_packs/</code>; pack lint errors=0; run report <code>docs/run_reports/2026-07-09-p2034-broad-packs.md</code></td> </tr> <tr> <td>CODEX-BRIDGE</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Make the Claude Code → Codex bridge durable, full-session capable, and process-safe</td> <td>Root <code>AGENTS.md</code>; tracked Claude subagent + <code>/codex</code> command; protocol checker; Claude-approved live <code>codex</code> + same-thread <code>codex-reply</code> smoke; report <code>2026-07-09-claude-codex-mcp-bridge.md</code></td> </tr> <tr> <td>RESUME-CP5</td> <td>P0 Safety</td> <td>2026-07-09</td> <td>Resume and complete the CP-5 pre-campaign review session</td> <td>7 PRs merged (#22..#28); stop card CLEARED; CP-6 dispositions in the stream log; run report <code>2026-07-09-cp5-resume.md</code>; suite 822 OK</td> </tr> <tr> <td>P2-026</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>D-033 strict legacy-bypass close (frozen six-identity allowlist)</td> <td>PR #22; live-gated 6/6 corpus + tamper-fails + spoof probe fails closed</td> </tr> <tr> <td>P2-025</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Campaign-runner expected-vs-realized prompt-hash check (+ runtime/validator closure)</td> <td>PRs #24 + #27; fail-closed with type-discriminated sidecar inference; live-gated classifier truth table; 48/48 real-tokenizer closures</td> </tr> <tr> <td>P2-010b-GATE</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Envelope-gate analysis script (E1-E4 + E5 advisory, D-036 verdicts, CLI)</td> <td>PR #23; live-gated on the real mock affine bundle incl. refusal cases</td> </tr> <tr> <td>P2-027-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Bundle-pack publication tooling (pack + one-command verify)</td> <td>PR #25; live pack→verify→tamper→verify(2)</td> </tr> <tr> <td>CAPTURE-HARDENING</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Pre-campaign capture: output token IDs, fail-closed sampler pin (D-047 amendment), model weight hashing, env versions, hash-domain closure</td> <td>PR #27; live MLX gate incl. two full jw_mixed suite runs</td> </tr> <tr> <td>P2-012-MANIFESTS</td> <td>P2 Next Slice</td> <td>2026-07-09</td> <td>Tokenizer identity widening + real-tokenizer manifest regeneration</td> <td>PR #26; byte-identical double-regen; counts 512/512</td> </tr> <tr> <td>ADVISOR-SITE</td> <td>P4 Polish</td> <td>2026-07-09</td> <td>Advisor status site + suite_next draft-spec packet landing (D-051)</td> <td>PR #28; stop-card sha-verified intact; site regenerated with real renderer</td> </tr> <tr> <td>P2-018</td> <td>P4 Polish</td> <td>2026-07-08</td> <td>Deploy the site as a shareable Lakebed capsule with live GitHub freshness</td> <td>Live at <a href="https://quiet-signal-6af8833395.lakebed.app">https://quiet-signal-6af8833395.lakebed.app</a>; <code>scripts/pack_capsule.py</code> + <code>site_capsule/</code>; per-source drift vs <code>main</code>, fails soft; run report <code>2026-07-08-lakebed-deploy.md</code></td> </tr> <tr> <td>P2-021</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Drift sentinels + block-position covariates in the 2M generator</td> <td>PR #15 (merged 8765ee1); fail-loud sentinel manifest; campaign-log covariate echo; run report <code>2026-07-08-suite-science-expansion.md</code></td> </tr> <tr> <td>P2-017</td> <td>P2 Next Slice</td> <td>2026-07-08</td> <td>Honest per-source site provenance stamps</td> <td>PR #13 site-observatory rewrite: <code>git log -1 -- &lt;source&gt;</code> per page + <code>+ uncommitted</code> dirty marker; parser-tested; run report <code>2026-07-08-site-observatory.md</code></td> </tr> <tr> <td>P2-011</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>D-014 cross-repetition uncertainty (aggregate engine + manifest enrichment)</td> <td>PR #6; lead-verified real n=3 experiment, byte-identical re-derivation; run report 2026-07-07-parallel-streams-session.md; C-006 trace</td> </tr> <tr> <td>P2-008</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Mock telemetry × SystemClock strictly-interior stamping</td> <td>PR #5; live-verified at 1 Hz real-MLX; 20 Hz workaround retired</td> </tr> <tr> <td>P2-009</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Rich telemetry + idle-quality gate + environment capture</td> <td>PR #4 + INT-002 (8856c04); idle gate first live true positive</td> </tr> <tr> <td>2M-TOOLING</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>Campaign matrix generator + resumable sequential runner</td> <td>PR #3 + INT-001 (a05e54d); dry-run/resume/crash flows lead-verified</td> </tr> <tr> <td>KV-SIZE</td> <td>P3 Research Expansion</td> <td>2026-07-07</td> <td>Stage 3.0.0 kv-size helper (module + CLI verb)</td> <td>PR #2; anchors verified against both mirrored models</td> </tr> <tr> <td>FLAGSHIP-001</td> <td>P2 Next Slice</td> <td>2026-07-07</td> <td>User-directed flagship benchmark: Qwen3.5-122B-A10B-4bit on the M3 Max</td> <td>3/3 strict-valid bundles: ~304.0 J gross / ~298.7 J idle-sub per 512-tok request, 582-585 mJ/generated-output-token idle-sub (mean 583.4), 46 tok/s, gross CV 0.3% within one warm-cache session; legacy L1 (bases corrected 2026-07-09, C-027); run report <code>2026-07-07-flagship-qwen35-122b.md</code>; first Q4 data point</td> </tr> <tr> <td>P1-002</td> <td>P1 Phase Gate</td> <td>2026-07-06</td> <td>Mac-local Phase 1 telemetry/runtime evidence — sample captured, fields pinned, D-004 sudoers installed + <code>sudo -n</code> verified, MLX installed</td> <td>Phase 1 exit checklist instrumentation section; fixture committed; live 2I run</td> </tr> <tr> <td>P2-003</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Mac MLX + powermetrics vertical slice (2G, 2H, 2I) — <strong>first real energy numbers</strong></td> <td>Commits <code>3eb0acd</code>/<code>26dca41</code>/<code>b4d4173</code>; 3/3 strict-valid bundles: ~47.2 J gross / ~44.4 J idle-sub per 512-token request, 79.4-90.5 mJ/generated-output-token idle-sub (mean 86.8), 257 tok/s, TTFT ~94 ms; legacy L1 (bases corrected 2026-07-09, C-027; the old 77-88 figure used the prompt+output denominator); run reports 2026-07-06 (buildout, 2H, 2I)</td> </tr> <tr> <td>P0-002</td> <td>P0 Safety</td> <td>2026-07-06</td> <td>Measurement-corpus backup protocol (R-016) — interim destination per user direction</td> <td><code>scripts/backup_runs.sh</code>; restore test green (<code>validate-bundle</code> on restored copy); protocol in R-016; follow-up P0-003 tracks the real destination</td> </tr> <tr> <td>P3-001</td> <td>P3 Research Expansion</td> <td>2026-07-06</td> <td>Background/related-work draft (Phase 4 Stage 4.6)</td> <td><code>docs/phase_4/related_work_draft.md</code>: 11 sources, independently verified citations, positioning claims honestly adjusted (claims 1-2 narrowed, claim 3 stands)</td> </tr> <tr> <td>2G (P2-003 part)</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>MLX runtime adapter — first real generation traces on the M3 Max</td> <td>Commit <code>3eb0acd</code>; succeeded bundle <code>example-mac-mlx-mock-telemetry</code> (TTFT 81.5 ms, 265.8 tok/s, <code>--strict</code> valid); suite 230 OK both interpreters; implemented by Codex via <code>scripts/codex-bridge</code>, reviewed + live-verified by Claude</td> </tr> <tr> <td>DOC-006</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Independent status-review intake (user-directed): all three findings verified and fixed — P1 event-timestamp hardening, P2 <code>validate-bundle --strict</code> (D-030), P3 adapter raw-write helper</td> <td>Review <code>2026-07-06-project-status-review.md</code>; fixes run report <code>2026-07-06-status-review-fixes.md</code>; 226 tests OK</td> </tr> <tr> <td>P2-007</td> <td>P2 Next Slice</td> <td>2026-07-06</td> <td>Slice 2N pre-hardware hardening (all nine items, three commits)</td> <td>Run report <code>2026-07-06-slice-2n-pre-hardware-hardening.md</code>; D-024..D-029; 216 tests OK; exit-checklist 2N row closed</td> </tr> <tr> <td>DOC-005</td> <td>P4 Polish</td> <td>2026-07-06</td> <td>External architecture review intake (user-directed): D-024 RunContext, D-025 shared bundle reader, node-worker protocol contract, 2N items 8-9</td> <td>Run report <code>2026-07-06-architecture-review-intake.md</code>; <code>docs/contracts/node_worker_protocol.md</code></td> </tr> <tr> <td>DOC-004</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Agent playbook (user-directed): per-mission execution guides for all remaining steps</td> <td><code>docs/agent_playbook.md</code>; pointers in <code>README.md</code>/<code>AGENT_PLAN.md</code>; Stage 4.6 seeded with named competitor set</td> </tr> <tr> <td>P0-001</td> <td>P0 Safety</td> <td>2026-07-05</td> <td>Move repo off iCloud-synced Desktop (R-017)</td> <td>New path <code>~/code/CapstoneRivoire/Capstone</code>; git + suite verified green at the new location; recorded in <code>RUN_STATE.md</code></td> </tr> <tr> <td>DOC-003</td> <td>P4 Polish</td> <td>2026-07-05</td> <td>Docs/meta-layer cleanup (user-directed): drift fixes, D-023 status consolidation, plan/guide dedup, R-016/R-017, Slice 2N + Stage 4.6 planned</td> <td>Run report <code>2026-07-05-docs-meta-cleanup.md</code>; D-023; risk register updated</td> </tr> <tr> <td>P2-001</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Mock vertical slice: slices 2A-2E</td> <td>Harness runs end-to-end; <code>validate-bundle</code> green; CI mock e2e step added; 169 tests. <code>joulewise/{bundle,clock,controller,reduce,cli}.py</code> + <code>adapters/</code>; run report <code>2026-06-12-phase-2-mock-vertical-slice.md</code></td> </tr> <tr> <td>P2-002</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Repetitions + experiment manifests (slice 2F)</td> <td><code>run_experiment</code> + cooldown gate; 3-rep + kill-after-rep-2 + cooldown tests; manifest per D-005. Same run report</td> </tr> <tr> <td>P2-J</td> <td>P2 Next Slice</td> <td>2026-06-12</td> <td>Static report generator (slice 2J)</td> <td><code>joulewise/report.py</code>; matplotlib behind <code>[analysis]</code>; graceful structured failure when absent; tests skip cleanly without the extra</td> </tr> <tr> <td>P1-005</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Hailo feasibility verdict</td> <td><code>unsupported_workload</code> from official-source desk research; recorded in the Phase 1 exit checklist Hailo section</td> </tr> <tr> <td>P1-007</td> <td>P1 Phase Gate</td> <td>2026-06-12</td> <td>Phase 2 readiness review</td> <td>Recorded in the Phase 1 exit checklist; verdict &quot;mock-first Phase 2 may begin&quot;</td> </tr> <tr> <td>Q-000</td> <td>P0 Safety</td> <td>2026-06-09</td> <td>Resolve the local <code>Energy_Benchmark_Architecture.docx</code> deletion decision</td> <td>User confirmed the Word doc was unrelated; deletion committed in <code>a5d7404</code></td> </tr> <tr> <td>PLAN-001</td> <td>P1 Phase Gate</td> <td>2026-06-09</td> <td>Build evidence-shaped plans for Phases 2-5 (user-directed)</td> <td>Per-phase plan + exit-checklist docs; <code>docs/decision_log.md</code> (D-001..D-019); <code>docs/risk_register.md</code>; <code>docs/milestones.md</code>; methodology/bundle-layout amendments; <code>AGENT_PLAN.md</code> restructured as index; run report <code>docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md</code></td> </tr> <tr> <td>CI-001</td> <td>P2 Next Slice</td> <td>2026-06-09</td> <td>Add core-tests CI workflow (D-017)</td> <td><code>.github/workflows/ci.yml</code>; extended 2026-06-12 with the mock end-to-end run</td> </tr> <tr> <td>DOC-001</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Unify Phase 1 doc scheme with Phases 2-5 (user-directed)</td> <td><code>docs/phase_1/</code> reduced to <code>phase_1_plan.md</code> + <code>phase_1_exit_checklist.md</code>; contracts moved to <code>docs/contracts/</code>; run report <code>docs/run_reports/2026-06-09-phase-1-doc-unification.md</code></td> </tr> <tr> <td>DOC-002</td> <td>P4 Polish</td> <td>2026-06-09</td> <td>Add advisor-facing status/plan/architecture doc + audit original sketch (user-directed)</td> <td>Root <code>PROJECT_STATUS.md</code>; run report <code>docs/run_reports/2026-06-09-advisor-status-doc.md</code></td> </tr> </tbody></table></div> <h2 id="shelved-follow-ups-with-triggers-c-027-disposition-ledger-rev-10">Shelved Follow-Ups With Triggers (C-027 disposition ledger — REV-10)</h2> <p>Previously promised follow-ups whose queue rows had silently died; each now has an explicit disposition:</p> <ul> <li><p>D-013 SSH-controlled vs co-resident controller comparison — SHELF, trigger: first 2K live session (validation cell rides that session).</p> </li> <li><p>Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF, trigger: Window-A calibration data exists (P2-015 output feeds it).</p> </li> <li><p><code>dvfm_states</code> slimming option — SHELF, trigger: bundle-size pain during the 2M campaign; otherwise declined as premature.</p> </li> <li><p>Cold-load / model-load-energy capture — DECLINED for the capstone scope (CP-5 deferral made permanent unless an AP row claims it; warm-cache protocol is the declared scope).</p> </li> <li><p>CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).</p> </li> <li><p>DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).</p> </li> </ul> <h2 id="current-do-not-do-yet-list">Current Do-Not-Do-Yet List</h2> <ul> <li>(satisfied 2026-06-12) The mock bundle/reducer path and report generator now exist; dashboard/report work is no longer blocked.</li> <li>(satisfied 2026-06-12) The mock lifecycle is runnable, so live MLX/powermetrics implementation may proceed once its hardware gates open (P1-002 + D-016); follow <code>docs/phase_2/hardware_slice_implementation_guide.md</code>.</li> <li>(resolved 2026-06-12) Hailo feasibility has a verdict (<code>unsupported_workload</code>); do not implement a Hailo backend — report it as an applicability finding.</li> <li>Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in D-008; implementation waits).</li> <li>Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware pairings, or borrow-window scheduling before 2M baselines and the Stage 3.0 verdicts exist (C-007 wording fix; was previously stated as a blanket Phase 3 hold that contradicted the queue).</li> <li>Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the rehearsed runbook exist (R-006).</li> <li>Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has produced data.</li> <li>Do not close D-016 (model selection) without P1-001 supervisor scope or an explicit user go-ahead.</li> <li>(satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own gates (D-016 + <code>[mac]</code> install; privileged sample + D-004 sudoers) open — build on the post-2N seams (RunContext raw evidence, D-026 markers, D-027 rail rows, 2N.3 observed-token fallback).</li> </ul> <h2 id="queue-maintenance">Queue Maintenance</h2> <p>At the end of substantial work:</p> <ul> <li>Update live status, rank, dependencies, and new tasks in <code>docs/process/state_kernel.json</code>.</li> <li>Remove terminal tasks from the kernel only after their owning completion evidence supports closure; preserve the dated Completed row here.</li> <li>Run <code>python3 scripts/gen_state.py</code>; never hand-edit generated queue or restart rows.</li> <li>Keep hand-authored edits here to policy, completed/history records, and non-selection context.</li> </ul> <h2 id="current-queue">Current Queue</h2> <p>The generated region below is the sole live queue and source of truth for work selection. Edit the kernel and regenerate; do not hand-edit its rows.</p> <p>Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see <code>docs/contracts/analysis_plans.md</code> §Required fields.</p> <p>Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see <code>docs/specs/c027/rpt-001_report_vertical_slice.md</code> §0.4 and <code>docs/contracts/publication_privacy.md</code> §Publication boundary.</p> <!-- BEGIN GENERATED: state-kernel current-queue --> <!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. --><p>Source of truth for work selection: <a href="docs/process/state_kernel.json">state kernel</a> (updated 2026-07-25).</p> <p>Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.</p> <div class="table-scroll"><table> <thead> <tr> <th>Rank</th> <th>ID</th> <th>Priority</th> <th>Status</th> <th>Task</th> <th>Evidence / Acceptance</th> </tr> </thead> <tbody><tr> <td>E1</td> <td>P1-008</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).</td> <td>Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: <a href="docs/milestones.md">Milestones + R-012</a>. Acceptance: <a href="docs/process/state_kernel.json">P1-008 acceptance</a>. Note: R-012 is the biggest active management risk for an undergrad timeline.</td> </tr> <tr> <td>E2</td> <td>P2-027</td> <td>P2 Next Slice</td> <td>READY [ED-EXTERNAL]</td> <td>Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party.</td> <td>Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-020 + C-027 NEG-9</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-027 acceptance</a>. Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL.</td> </tr> <tr> <td>E3</td> <td>P1-001</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Capture supervisor approval and scope notes.</td> <td>Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: <a href="docs/risk_register.md">R-001</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped.</td> </tr> <tr> <td>E4</td> <td>P1-003</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method.</td> <td>Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: <a href="docs/decision_log.md">D-018/C-003</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Elevated value: gates Q6 boundary sensitivity (C-003).</td> </tr> <tr> <td>E5</td> <td>P1-004</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method.</td> <td>Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: <a href="docs/risk_register.md">R-011</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Partial.</td> </tr> <tr> <td>E6</td> <td>P1-006</td> <td>P1 Phase Gate</td> <td>READY [ED-EXTERNAL]</td> <td>Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L).</td> <td>Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: <a href="docs/phase_2/hardware_slice_implementation_guide.md">Remote gate / NV-GATE-2</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>.</td> </tr> <tr> <td>Q1</td> <td>P2-015</td> <td>P2 Next Slice</td> <td>PARTIAL; READY [QUIET-MAC]</td> <td>Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.</td> <td>Reducer-0.5.2/0.6.2 strict-valid calibration bundles; per-metric floor_abs_j and floor_cmp_j; governed idle uncertainty retained; calibration manifest hash cited by later reports. Evidence: Versioned strict-valid calibration bundles; Per-metric/window-class floor_abs_j + floor_cmp_j; Calibration manifest hash cited by later reports. Authority: <a href="docs/phase_2/detection_floor.md">D-054 + detection floor spec</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Fence: Claim-bearing collection requires fresh 59-pulse protocol-v3 calibration BRACKETING the window (consumed max(B_pre,B_post)); floor artifacts are claim-licensing only from same-custody-session governed extraction until FLOOR-BIND-01 closes (D-078 clause 8 (L1) + bracketing ruling). Note: PR #79 instrument repair and PR #85 SCREEN+BUDGET rules are merged; the start gate is one clean quiet window executed per docs/phase_2/window_runbook.md.</td> </tr> <tr> <td>Q2</td> <td>P2-006</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors measured first) [QUIET-MAC]</td> <td>Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.</td> <td>Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: <a href="docs/phase_2/phase_2_plan.md">Phase 2 plan + analysis plans</a>. Acceptance: <a href="docs/phase_2/phase_2_exit_checklist.md">Phase 2 exit checklist</a>. Note: Software interpretation gates are satisfied; execution remains blocked until P2-015 Window-A floors complete.</td> </tr> <tr> <td>Q3</td> <td>P2-010</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (quiet-window tail available after floors) [QUIET-MAC]</td> <td>P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail.</td> <td>joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: <a href="docs/contracts/analysis_plans.md">AP-5 + affine stream log</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-010 acceptance</a>. Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains.</td> </tr> <tr> <td>Q4</td> <td>P2-019</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6).</td> <td>Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: <a href="docs/contracts/analysis_plans.md">AP-1</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-019 acceptance</a>.</td> </tr> <tr> <td>Q5</td> <td>P2-020</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC]</td> <td>Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts.</td> <td>Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: <a href="docs/contracts/analysis_plans.md">AP-6 + D-046</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-020 acceptance</a>. Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6).</td> </tr> <tr> <td>Q6</td> <td>P2-012</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC]</td> <td>Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases.</td> <td>Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: <a href="docs/contracts/analysis_plans.md">AP-4 + D-039/D-040</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-012 acceptance</a>. Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27).</td> </tr> <tr> <td>Q8</td> <td>P2-046B</td> <td>P1 Phase Gate</td> <td>READY [QUIET-MAC]</td> <td>Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts.</td> <td>Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C6</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-046B acceptance</a>. Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution.</td> </tr> <tr> <td>Q9</td> <td>P2-047B</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist), P2-047A (frozen controller-overhead harness exists) [QUIET-MAC]</td> <td>Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict.</td> <td>Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047B acceptance</a>.</td> </tr> <tr> <td>A0</td> <td>P2-035</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-015 (P2-015 detection floors measured) [AGENT]</td> <td>RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).</td> <td>Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: <a href="docs/specs/rq_energy_variance_design.md">RQ-ENERGY-VARIANCE candidate design</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-035 acceptance</a>. Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine).</td> </tr> <tr> <td>A3</td> <td>FLOOR-BIND-01</td> <td>P1 Phase Gate</td> <td>READY [AGENT]</td> <td>Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.</td> <td>Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: <a href="docs/decision_log.md">D-078 clause 8 (confirmation round 9, registered limitation L1)</a>. Acceptance: <a href="docs/process/state_kernel.json">FLOOR-BIND-01 acceptance</a>. Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed.</td> </tr> <tr> <td>A4</td> <td>AXI-SB-ADAPTER</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims.</td> <td>The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: <a href="docs/specs/axi/sb_static_batch_verdict.md">AXI-SB verdict document (supported; mint-on-supported follow-on)</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SB-ADAPTER acceptance</a>. Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A6</td> <td>AXI-SD</td> <td>P2 Next Slice</td> <td>READY [AGENT]</td> <td>Prepare the matched dense/MoE pair proposal with the consult&#39;s pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT.</td> <td>A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016&#39;s cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-D</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SD acceptance</a>. Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership).</td> </tr> <tr> <td>A7</td> <td>AXI-SE</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (P2-015 publishes Window-A floors before AXI analysis plans are finalized) [AGENT]</td> <td>Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult&#39;s floor and ownership closures.</td> <td>The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A&#39;s gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: <a href="docs/axi-handoff.md#4-work-program-post-audit-clearance-streams">AXI handoff work program S-E</a>. Acceptance: <a href="docs/process/state_kernel.json">AXI-SE acceptance</a>. Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership).</td> </tr> <tr> <td>A16</td> <td>P3-000</td> <td>P3 Research Expansion</td> <td>BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT]</td> <td>KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8).</td> <td>Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: <a href="docs/decision_log.md">D-035/D-036</a>. Acceptance: <a href="docs/phase_3/phase_3_exit_checklist.md">Phase 3 exit checklist</a>. Note: 3.0.1 complete and merged (PR #9, replay_supported).</td> </tr> <tr> <td>A17</td> <td>P2-022</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT]</td> <td>Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported).</td> <td>3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/contracts/adapter_contracts.md">Adapter contract</a>. Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission.</td> </tr> <tr> <td>A18</td> <td>P2-023</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT]</td> <td>HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy.</td> <td>Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: <a href="docs/decision_log.md">D-041 (post-2M gate)</a>. Acceptance: <a href="docs/research_question_bank.md">RQ bank import-smoke design</a>. Fence: No pass@k, accuracy, or capability claim (D-041).</td> </tr> <tr> <td>A19</td> <td>P2-024</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (2M reductions identify floor/MDE headroom), P2-015 (Window-A floors measured) [AGENT]</td> <td>Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC].</td> <td>Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: <a href="docs/research_question_bank.md">C-015 + RQ bank</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-024 acceptance</a>.</td> </tr> <tr> <td>A21</td> <td>P3-001b</td> <td>P3 Research Expansion</td> <td>BLOCKED — P2-006 (2M affine coefficients exist) [AGENT]</td> <td>Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049).</td> <td>AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: <a href="docs/decision_log.md">D-048/D-049</a>. Acceptance: <a href="docs/contracts/analysis_plans.md">Analysis plans (split row)</a>.</td> </tr> <tr> <td>A22</td> <td>P2-004</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES close: P1-001 [AGENT]</td> <td>Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding.</td> <td>Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: <a href="docs/decision_log.md">D-016</a>. Acceptance: <a href="docs/phase_1/phase_1_exit_checklist.md">Phase 1 exit checklist</a>. Note: Provisional small-model pick 2026-07-06 opens 2G.</td> </tr> <tr> <td>A23</td> <td>P2-005</td> <td>P2 Next Slice</td> <td>PARTIAL; READY; GATES live_promotion: P1-006 [AGENT]</td> <td>Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute.</td> <td>Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: <a href="docs/specs/c027/nv-gate-2_live_promotion.md">NV-GATE-2 live-promotion spec</a>. Acceptance: <a href="docs/phase_1/2k_live_verification_checklist.md">2K live verification checklist</a>. Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open.</td> </tr> <tr> <td>A24</td> <td>P2-016</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-006 (the 2M corpus exists) [AGENT]</td> <td>Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment.</td> <td>Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: <a href="docs/reviews/2026-07-09-c027-whole-project-review.md">C-011 ledger + C-027 (post-2M umbrella)</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-016 acceptance</a>. Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake.</td> </tr> <tr> <td>A25</td> <td>P2-047A</td> <td>P2 Next Slice</td> <td>BLOCKED — P2-015 (Window-A floors exist before overhead design is frozen) [AGENT]</td> <td>Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes.</td> <td>A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: <a href="docs/reviews/2026-07-10-hardening-adjudication.md">Hardening adjudication C7</a>. Acceptance: <a href="docs/process/state_kernel.json">P2-047A acceptance</a>. Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7).</td> </tr> <tr> <td>A29</td> <td>DOC-008-REFLECTION</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6.</td> <td>Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 reflection-protocol retirement</a>. Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence).</td> </tr> <tr> <td>A30</td> <td>DOC-008-STATUS</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8.</td> <td>Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 PROJECT_STATUS compaction</a>. Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence).</td> </tr> <tr> <td>A31</td> <td>DOC-008-INTAKE</td> <td>P4 Polish</td> <td>READY [AGENT]</td> <td>Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9.</td> <td>Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake and procedure reconciliation</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 intake reconciliation</a>. Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence).</td> </tr> <tr> <td>A32</td> <td>DOC-008</td> <td>P4 Polish</td> <td>PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT]</td> <td>Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked.</td> <td>Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 state-kernel specification</a>. Acceptance: <a href="docs/specs/c027/doc-008_state_kernel.md">DOC-008 required outcomes</a>. Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live.</td> </tr> <tr> <td>A33</td> <td>P2-050</td> <td>P3 Hardening Candidates</td> <td>READY [AGENT]</td> <td>Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2.</td> <td>Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives i </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>TASK_QUEUE.md · commit de665ea · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
docs/specs/c027/rpt-001_report_vertical_slice.md:328:- the measurement-boundary table;
docs/paper/related_work_draft.md:3:JouleWise lies at the intersection of inference-energy benchmarking, software power measurement, experimental metrology, and split inference. Its central difference is one of emphasis: the measurement instrument is the product, while model and deployment comparisons are demonstration studies. The instrument reports an energy verdict for a complete, declared measurement window; records the raw observations and their chain of custody; freezes the comparison and acceptance rules before seeing the result; and declines to make a claim when an effect falls below its detection floor, the smallest effect it can distinguish under the stated conditions. This framing makes uncertainty, timing attribution, drift, and evidence integrity part of the result rather than implementation details behind a leaderboard value.
docs/paper/draft-v1.md:5:Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.
docs/run_reports/2026-07-30-paper-outline-v1.md:16:- Hook: LLM energy numbers are everywhere (leaderboards, policy debates,
docs/run_reports/2026-07-30-sweep-cv-paths.md:48:**4. Leaderboard/site path.** The [ML.ENERGY leaderboard](https://ml.energy/) is the proof that such artifacts get cited (it became a **NeurIPS 2025 Datasets & Benchmarks spotlight paper**, is cited by follow-on benchmarking papers, and anchored a NeurIPS tutorial with NVIDIA/Google/Meta). But it is a *funded multi-person lab initiative* (Mozilla Technology Fund, Laude Institute support). A solo undergrad running a continuously-updated leaderboard is a maintenance trap: every new model release creates silent obligation, and a stale leaderboard is a negative signal. The cheap variant that keeps ~80% of the value: a **static results page with error bars** ("J/token for N local models on M-series, with detection floors"), versioned, dated, and linked from the tool README — a snapshot, not a service.
docs/run_reports/2026-07-30-sweep-cv-paths.md:80:| 6 | Live maintained leaderboard | **High, unbounded** | Moderate if fresh, **negative if stale** | Weak unless it becomes a paper (ML.ENERGY needed a funded lab to get there) | Perpetual maintenance; solo undergrad vs. funded Michigan lab | — |
docs/run_reports/2026-07-30-sweep-cv-paths.md:85:**Ship the tool + blog post first (fall 2026), submit the workshop paper second (winter/spring 2027), convert repro discipline into an ICPE artifact badge if the dates cooperate.** These three compound: the tool release makes the workshop paper *stronger* (reviewers can install what the paper describes — rare and disarming), the paper makes the tool *credible* (the validation story becomes citable), and the badge or well-documented repo covers whichever audience the other two miss. The niche is verifiably open — the only existing Apple Silicon ML-energy library has 8 stars and a README disclaiming its own accuracy — and the exact skillset appears verbatim in current NVIDIA and Apple new-grad/perf-power postings, which is the strongest industry-side evidence found. Skip the live leaderboard (funded-lab economics, solo-maintenance trap) in favor of a dated static results page; skip CCGrid (wrong audience, highest bar, earliest deadline). One deliberate gap to accept: nothing lands as "published" before Dec 2026 grad deadlines, so if Fall 2027 PhD entry matters, the EuroMLSys/ICPE submission should be timed to be "under review" by application season — otherwise the calendar is comfortable.

exec
/bin/zsh -lc "sed -n '270,455p' docs/council_log.md; sed -n '930,1010p' docs/decision_log.md; sed -n '90,125p' docs/contracts/token_normalization.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
examiner's rewrite were actually incompatible.

1. **"Nobody publishes joules/token for local inference" — KILLED by the
   steelman lens itself, replaced by the auditability claim.** Steelman
   brief asserted the missing-public-data angle; the steelman lens
   fact-checked its own charge and found MLPerf Power, TokenPowerBench,
   and ML.ENERGY-style datacenter benchmarks exist. Reasoning: an
   importance case built on a falsifiable "nobody does X" collapses on
   first review; the true differentiator is that JouleWise numbers are
   auditable FROM RAW EVIDENCE (bundle + strict re-reduction), which no
   named competitor offers for local inference. Outcome: the preamble
   leads with auditability, not novelty-of-topic. Dissent: none.

2. **MoE active-params scaling (6.7× → 6.7× mJ/token, flat power) —
   SCOPED from "finding" to "hypothesis + designed experiment".**
   Steelman position: the 122B result is the flagship story of the
   unified-memory measurement window. Attack (examiner #8): one model
   pair, one quant, one runtime, one SoC, and the two models differ in
   family, reasoning-mode, and total params simultaneously — "scaling
   law" language is unearned; total-vs-active params, KV size, and
   runtime version are all uncontrolled confounds. Reasoning that
   decided it: the observation is real and striking, but its epistemic
   status is one data point on a line with two points; the honest form
   is the EXPERIMENT that would make it a claim. Outcome: killed the
   scaling-law WORDING; promoted the minimal defensible design to Tier-1
   RQ-T1.1 (4-6 model points, dense + MoE controls, same quant recipe and
   pinned runtime, fixed shapes, n≥5, interleaved, fitted with
   uncertainty; claim template "evidence for active-parameter scaling on
   MLX/M3 Max", never "MoE models scale with active params"). Dissent:
   none — steelman's own text had already hedged ("simple, falsifiable
   pattern").

3. **Carbon labels — KILLED as a near-term application; the
   local-vs-cloud crossover QUESTION survives.** Steelman/apps position:
   energy labels and carbon accounting are a natural use. Attack
   (examiner #1, #7): powermetrics is vendor-MODELED rail telemetry at a
   boundary that excludes DRAM-at-wall/display/PSU; a carbon number
   derived from it is unauditable at exactly the step the whole harness
   exists to make auditable, and grid-intensity assumptions compound it.
   Reasoning: the kill is about the LABEL (a public absolute claim);
   the underlying question (when is local inference energy-cheaper than
   a datacenter round trip) survives because it can be honestly framed
   as boundary-explicit, wall-meter-calibrated, and
   assumption-documented — the harness supplies the local side with real
   error bars, which is the currently-missing half. Outcome: carbon
   labels moved to "requires wall meter + stated grid assumptions,
   phrase as 'measured local inference energy on named boundary'";
   crossover economics kept as Tier-2 (wall meter gate). Dissent: none.

4. **Cross-device leaderboard / public model cards — SCOPED to an
   internal→public ladder.** Apps position: joules/token next to quality
   scores, public leaderboard on identical hardware. Attack (examiner
   #7, #3): one lab, one machine, no cross-lab reproduction, and
   boundary-inconsistent columns (SoC rails vs GPU board) would make a
   public table exactly the kind of unauditable artifact the project
   critiques. Reasoning: the defect is prematurity, not concept —
   pinned-condition internal tables are defensible today, and the
   path to public credibility is locked methodology + reference
   workloads + a second lab reproducing. Outcome: kept, with the ladder
   (internal tool → published methodology → cross-lab table) written
   into the application entry. Dissent: none.

5. **CI energy-regression gates — SCOPED with preconditions.** Attack
   (examiner #2, #7): run-to-run CV 0.3-1.4% today but across reboots /
   OS updates / charger states the variance envelope is unknown; a gate
   thresholded below the detection floor generates noise-failures and
   discredits the tool. Reasoning: the application is sound and is the
   natural consumer of the methodology-centerpiece detection-floor work
   already in the bank; the gate must be defined in units of the
   MEASURED floor. Outcome: kept as a top-3 application with
   preconditions (pinned host, environment snapshots from P2-009,
   baseline-refresh policy, threshold ≥ measured detection floor).
   Dissent: none.

6. **Iso-quality architecture comparisons — SCOPED into the C-004
   quarantine.** RQ-generator position: dense-vs-MoE at iso-quality is a
   publishable frontier. Attack (examiner #6): "iso-quality" smuggles
   back the killed intelligence-per-joule problem the moment quality is
   a free-form eval score; scorer choice, stopping policy, and
   answer-length distributions become unacknowledged experimental
   variables. Reasoning: C-003/C-004 already adjudicated this lane —
   the surviving form is the controlled-envelope ladder
   (affine_mod_ladder_v1) where difficulty is designed to hold token
   budget constant and correctness is an annotation. Outcome: RQ kept
   but rewritten to require either the quarantined ladder or
   benchmark-band MATCHING (pairing models others have scored, without
   JouleWise running the eval), and the claim template fixed to "energy
   per correct answer on this controlled ladder". Dissent: none — this
   re-affirms a standing kill rather than re-litigating it.

7. **Per-token / fine-timing claims — KILLED (re-affirmed).** Several
   candidate shapes (KV decode drift per token, sub-100 ms phase
   attribution, short-prompt prefill energy) run into the ~9 Hz sampler
   vs ~4 ms token cadence. Reasoning: standing C-003 rule; the examiner
   extended it to phase windows generally — any window with fewer than
   several samples reports "unidentifiable", not joules (this is
   exactly the queued identifiability-flags feature). Outcome: all such
   questions carry a CHUNKED-window methodology note; the 0.03 J
   prefill number is reported as "unresolved at this resolution", not
   as a measurement. Dissent: none.

8. **Small-effect questions at n=5 — SCOPED with a power precondition.**
   Attack (examiner #2): sampling-strategy overhead, small runtime
   deltas, and minor DVFS effects are plausibly below the ~1% CI width
   n=5 buys at the observed CV. Reasoning: rather than dropping the
   questions, order them behind the detection-floor measurement and
   prescribe the rescue design (paired ABBA/interleaved runs, n=10-20
   for ~1% effects — cheap on this instrument at 30-75 bundles/hour).
   Outcome: affected Tier-1 questions carry an explicit "requires
   detection floor first; n≥10 paired" note. Dissent: none.

9. **Single-machine generalizability — SCOPED by claim-type taxonomy.**
   Attack (examiner #3): every result is "one M3 Max in one apartment".
   Reasoning: the defensible survivors are (a) instrument claims, (b)
   within-target structure (ratios, decompositions, rankings on one
   box), and (c) existence proofs (ANE dark; contamination detectable);
   population claims need a second unit or second lab — which is what
   Tier 3 acquisitions are FOR. Outcome: the agenda's claim templates
   use "on this M3 Max / MLX / powermetrics" wording throughout, and
   Tier 3 names "a second M-series unit" as the cheapest
   generalizability purchase. Dissent: none.

10. **"The harness already supports X" wording — KILLED where X is
    queued.** Attack (examiner #9): uncertainty aggregation (D-014) is a
    dead field until P2-011; rich telemetry (P2-009), scored suite
    (P2-010), 2M matrix, remote targets, wall meter, and split runs are
    queued or planned, not landed. Reasoning: the steelman is a case for
    the INSTRUMENT + ROADMAP and must not misstate the present tense —
    exactly the drift the docs-consistency protocol exists to prevent.
    Outcome: the agenda's preamble and every RQ hardware line separate
    measured-today / queued / gated. Dissent: none.

11. **Boundary exclusions as DIRECTIONAL bias — ADOPTED as a
    methodology note on multiple RQs.** The examiner's sharpest novel
    point: the Mac SoC boundary doesn't just offset absolute numbers,
    it can BIAS COMPARISONS whose conditions differ in unified-memory
    traffic (long-context, KV-heavy, memory-bound workloads
    underrepresented relative to wall). Reasoning: this elevates Q6
    (boundary sensitivity) from calibration chore to a gating
    dependency for several Tier-1/Tier-2 comparisons. Outcome:
    KV-economics and long-context RQs carry "boundary-directional-bias"
    threat notes; the wall meter's value statement in the agenda cites
    this, strengthening the case for closing P1-003. Dissent: none.

12. **Workload categories vs "token counts explain everything" — BOTH
    outcomes pre-registered.** Workload-designer position: category
    (chat/code/summarization/reasoning/extraction/multilingual) is a
    real energy axis via prefill:decode ratio, output-length
    distributions, and thinking-token inflation. Orchestrator applied
    the examiner's frame: at fixed token shape, category differences
    may collapse to nothing the instrument can resolve. Reasoning: the
    suite is designed so EITHER result is publishable — shape-matched
    synthetic controls paired with category exemplars make "energy/token
    is shape-determined, category-invariant" a strong reportable null,
    while thinking-token inflation (measured on the already-benchmarked
    reasoning flagship) is the category effect most likely to be large.
    Outcome: `jw_mixed_v1` adopted as the recommended starter suite
    with paired controls and greedy decoding + recorded stop reasons
    (EOS-bias audit inherited from C-004). Dissent: none.

## What the devil's advocate killed outright (summary list)

- Unqualified absolute-joule claims from modeled rails.
- Carbon LABELS (the application, near-term; the crossover question survives).
- "Scaling law" language from the 2-model MoE observation.
- Per-token energy claims and short-window phase joules (re-affirmed).
- Public cross-device leaderboards before wall calibration + cross-lab
  reproduction.
- Sub-detection-floor CI gate thresholds.
- Present-tense capability wording for queued features.
- (Re-affirmed standing kill) general intelligence-per-joule.

## Dissents

None outstanding. The lead notes one deliberate tension left in the
agenda rather than resolved: the steelman ranks the split-inference study
(Q1-Q3) among the top-3 claims while the examiner's hardware audit makes
it the most gate-dependent item in the entire agenda (links + second
node + borrow window). The agenda records both positions; the existing
feasibility-first Phase 3 ladder is already the mitigation.

## Process notes

- One operational failure: the fifth (workload) Codex lens initially
  hung on stdin when launched in background (`codex exec` read stdin);
  relaunched with `< /dev/null`. Worth folding into the codex-delegation
Two Python versions catch the realistic compat risks (3.11 floor vs 3.14
local) at trivial cost.

Consequences: `.github/workflows/ci.yml` added; Phase 2 Slice 2E adds the
mock end-to-end step to it; README badges optional, not required.

Revisit when: a self-hosted runner with GPU/Mac hardware ever materializes
(unlikely; not planned).

---

## D-018: Per-backend `power_w` definition and rail policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `power_trace.csv` has `power_w`, `source`, and optional `rail`
columns, but "power" means different physical boundaries on different
backends (SoC subsystems vs GPU board vs module input vs wall AC). Without a
fixed definition, cross-target comparisons silently compare different
quantities.

Options considered:

1. One `power_w` row per sample, backend decides what it means. Con: loses
   per-rail information; the meaning varies invisibly.
2. Per-rail rows only, reducers sum everything. Con: "everything" differs by
   backend; accidental double counting (e.g., a backend reporting both
   package and per-subsystem rails).
3. Per-rail rows preserved as reported, plus a per-backend *rail manifest*
   that names exactly which rails sum to the backend's canonical `power_w`
   for reduction, and a methodology table stating each backend's physical
   measurement boundary. powermetrics: cpu_power + gpu_power + ane_power
   (SoC subsystem proxy; excludes display, storage, PSU losses). nvidia-smi:
   board power as reported (GPU board only; excludes host). jetson_rails:
   VDD_IN preferred (module input) with the actually-used rail recorded.
   wall_meter: AC wall power (full system).

Decision: option 3.

Considerations: per-rail rows keep raw fidelity (Apple's per-subsystem split
is itself interesting data); the manifest makes the summation auditable and
fixable post hoc; the boundary table converts an implicit comparability
problem into an explicit, reportable limitation - cross-target absolute
comparisons must state boundaries, and wall-meter deltas (when the meter
exists, P1-003) calibrate the gap.

Consequences: telemetry adapters declare their rail manifest in
`device_metadata`; reducer sums per the manifest; methodology gains the
Measurement Boundaries section; the limitations section of the final report
inherits the boundary table.

Revisit when: a backend exposes a strictly better boundary (e.g., macOS adds
package-level wall-equivalent reporting).

---

## D-019: Mock adapters use simulated time via an injectable clock

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: reducer correctness tests need traces and events whose expected
energy is computable in closed form; the controller needs real time for real
runs. If mocks sleep through real seconds, tests get slow and flaky; if the
controller special-cases mocks, the lifecycle under test diverges from the
real one.

Options considered:

1. Mocks sleep in real time. Con: a 30 s idle window makes the test suite
   unusable; timestamp jitter breaks exact assertions.
2. Controller branches on mock backends. Con: the code path being tested is
   no longer the production path.
3. A minimal `Clock` protocol (`now() -> float`, `sleep(seconds)`) injected
   into the controller; `SystemClock` for real runs, `FakeClock` that
   advances instantly for tests and mock runs. Mock adapters compute
   deterministic timestamps/samples from the config and the injected clock;
   the controller code path is identical in both modes.

Any comparison across tokenizer families, or across model families with
different tokenizers, must do one of two things:

1. Carry companion denominators that are tokenizer-independent, such as
   `J/char`, `J/byte`, or semantic-matched pair denominators
   (FLORES-style same-content parallel items).
2. Avoid efficiency-ranking language entirely and remain descriptive.

Forbidden language:

| Forbidden language | Forbidden use | Allowed replacement |
|---|---|---|
| "more efficient per token" | Cross-tokenizer or cross-model-family ranking. | "lower `J/token` for [stack A] under tokenizer [name/revision/class/vocab size] than [stack B] under tokenizer [name/revision/class/vocab size], with request energy [direction/value] under [boundary]." |
| "better J/token" | Cross-family efficiency conclusion. | "different tokenizer-scoped `J/token` under [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size]; request energy is [direction/value] under [boundary]." |
| "cheaper tokens" | Treating tokens from different vocabularies as comparable work units. | "lower `J/char`, `J/byte`, or semantic-pair energy under the stated companion denominator." |
| Tokenizer-blind "energy per token" leaderboard language | Ranking stacks without naming tokenizer identity and request energy. | "tokenizer-scoped companion metrics for [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size], reported beside request energy." |
| Treating token counts as comparable work units across vocabularies | Any inference that equal token counts imply equal semantic, byte, or character work across tokenizers. | "same-content item energy" or "`J/char`/`J/byte` companion denominator, with tokenizer-scoped `J/token` only as context." |

Within one tokenizer identity, per-token comparisons still obey the claims
ladder, analysis registry, floor, order, and boundary rules. This contract
only prevents token denominators from being promoted into tokenizer-blind
efficiency units.

## Stack-Identity Table

Every reader-facing result claim governed by
`docs/contracts/claims_ladder.md` must carry stack identity across all
claims-ladder-governed surfaces: reports, slides, README/status prose,
captions, tables, and figures. Any exported or reused rendering of a governed
figure must carry the same stack identity in the rendered artifact or
immediately adjacent text, at minimum by naming a stack-identity table it
resolves to.

The table below defines the minimum fields and the expected
bundle/provenance surface when it is already known.

codex
# Before Joules Become Rankings: A Metrology-Complete Energy Label for Consumer LLM Inference

**Thesis:** An LLM energy number is interpretable only when accompanied by its measurement boundary, stack identity, calibration state, detection floor, uncertainty interval, and explicit claim verdict; JouleWise can define and empirically exercise such a label using its existing instrument and D-117 campaign.

## Project brief and steps

JouleWise already has the scientific foundation for this paper: a phase-resolved, single-request instrument on one named M3 Max/MLX/Qwen2.5-4-bit stack; in-window pulse calibration; the finding that roughly 30 ms of edge uncertainty across a roughly 33 W transition can misattribute about 1 J; detection floors composed from repeatability, worst-case attribution, and never-zero drift; separate floor-clearance and interval-direction gates; and a fail-closed, hash-bound protocol whose refusals are evidence. No result is currently citable as a valid minted claim: historical floor and contrast values remain diagnostic because their windows predate the issued acceptance regime. D-117 therefore replaces historical consumption with three prospective nights. Alpha collects 10 absolute and 40 null-comparison members for the 1.5B decode floor, with prefill extracted prospectively from the same 50 bundles; beta repeats this for 7B; gamma collects ten 1.5B-versus-7B decode ABBA blocks. Their budgeted occupancies, including 20% margin, are approximately 3.14, 3.24, and 2.80 hours. Before those nights, desk work must land the two-slot calibration-bracket session, acceptance-successor machinery, multi-plan/four-cell mint, prefill metric support, three-window regression, frozen campaign packs, and readiness packets. After alpha and beta pass, mint the combined four-cell floor artifact; then run gamma and apply the armwise maximum of the two decode floors plus the separate claim-side interval. For this paper, add a machine-readable and human-readable “nutrition label” renderer and validator, then apply it to every D-117 floor and demonstration result. Finally, conduct a preregistered desk audit of approximately 40 result rows—proposed, not power-derived—from the four nearest reporting systems discussed in the MVP draft, scoring whether each label field can be recovered. This is explicitly a metrology disclosure label, not a carbon label, battery-life estimate, certification, or public cross-device leaderboard.

## Contributions

1. **A falsifiable minimum reporting schema.** A result is complete only if it binds boundary, gross-J/request estimand, workload, phase, physical unit, OS/runtime/model/quantization/tokenizer identity, calibration bracket and status, floor decomposition, claim interval, gate verdict, and custody digest. The validator must reject every deliberately omitted mandatory field.

2. **A comparability decision procedure.** Pairwise comparison is permitted only when label fields establish the same boundary and compatible estimands; mutation tests must refuse boundary substitution, tokenizer-blind J/token ranking, point-repeatability substituted for the operative floor, and uncalibrated cross-boundary ranking.

3. **Five real label cells plus a contrast verdict.** The four D-117 floor cells—1.5B/7B × prefill/decode—and the decode contrast must be rendered directly from governed artifacts, with no hand-copied scientific numbers and byte-linked provenance.

4. **A reporting-practice audit.** Two independent coders apply the frozen rubric to the proposed 40-row literature/leaderboard sample. Report field-completeness rates and agreement; the critique fails if prevailing reporting already supplies the proposed mandatory evidence reliably.

## Experiment plan

Alpha and beta each contain 50 unique science bundles: 10 absolute members and ten four-member A/B/B/A null blocks, using the 128-prompt/512-output workload. Prefill is a preregistered rider over those exact bundles, not borrowed from a decode floor after collection. Gamma contains 40 members in ten ABBA blocks and tests `7B − 1.5B` decode energy.

The historical decode contrast is approximately 141.29 J on the registered phase metric—diagnostic only, not a claim—about 28 times the approximate 5 J practical bar. The prospective value is unknown, but a failure to clear would be scientifically important: the label would show that an apparently large table difference still lacks permission for directional language. Historical 128-token prefill diagnostics give a 5.81 J point contrast, but an uncertainty-adjusted lower edge near 4.0 J; it is therefore marginal, not evidence for a prefill direction. A 256-token arm projects roughly 11.6 J, about 2.3 times the bar, but this is an uncertain extrapolation because no long-prompt 7B corpus exists.

Base paper cost is exactly the three D-117 windows. A fourth, independently calibrated 256-token prefill window is optional for an ICPE-strengthened version only; it needs matching floor cells or a preregistered transport rule and likely about 110 core minutes plus bookends. No extension may be appended to gamma after freeze. Required new harness work is label serialization, completeness/comparability validation, and artifact-to-label rendering. It does not alter the frozen sequential, single-request boundary.

## Hardware and instrument needs

The owned M3 Max is sufficient; the RTX 3080 Ti and Jetsons are irrelevant. The WT310E is **not a dependency** because the label explicitly names the modeled `powermetrics` SoC boundary and withholds wall-energy claims. A borrowed WT310E would enable a later “wall-bridged total” label class, but still would not validate prefill/decode attribution.

## Venue fit and relationship to the MVP

This is an excellent capstone/CSCSU chapter and a credible performance- or sustainable-systems workshop paper. ICPE full-track fit is plausible only with the executable validator, the reporting audit, artifact-quality release, and preferably external adoption or wall-boundary extension; the label idea alone is too modest.

It reuses the MVP draft’s Sections 2–6 nearly intact: related-work gap, calibration, floor composition, fail-closed protocol, and instrument characterization. What is new is the reporting schema, comparability rules, mutation evaluation, audit, and D-117 results presented as worked labels rather than another leaderboard table.

## Risks and kill criteria

Kill it as a standalone paper before spending any extra night if the desk audit shows that the schema merely renames already-standard fields, if reviewers cannot apply the rubric reproducibly, or if the label produces no decision beyond existing paper prose. In that case, retain it as an MVP artifact/section. Do not fund the fourth window unless the 256-token plan has matching floor authority and a conservative projected interval clears 5 J. Failed D-117 windows, missing mint machinery, or unresolved custody bindings delay the paper; they must not be papered over with historical values.

## Relation to Ed’s original goals

This directly serves the energy-honest leaderboard/reporting axis and strengthens the modular harness by defining what every future experimental axis must disclose. It does not advance speculative decoding, MTP, MoE, KV variants, or split inference directly; instead, it supplies the reporting contract those later studies would need to make defensible energy comparisons.
tokens used
117,269
# Before Joules Become Rankings: A Metrology-Complete Energy Label for Consumer LLM Inference

**Thesis:** An LLM energy number is interpretable only when accompanied by its measurement boundary, stack identity, calibration state, detection floor, uncertainty interval, and explicit claim verdict; JouleWise can define and empirically exercise such a label using its existing instrument and D-117 campaign.

## Project brief and steps

JouleWise already has the scientific foundation for this paper: a phase-resolved, single-request instrument on one named M3 Max/MLX/Qwen2.5-4-bit stack; in-window pulse calibration; the finding that roughly 30 ms of edge uncertainty across a roughly 33 W transition can misattribute about 1 J; detection floors composed from repeatability, worst-case attribution, and never-zero drift; separate floor-clearance and interval-direction gates; and a fail-closed, hash-bound protocol whose refusals are evidence. No result is currently citable as a valid minted claim: historical floor and contrast values remain diagnostic because their windows predate the issued acceptance regime. D-117 therefore replaces historical consumption with three prospective nights. Alpha collects 10 absolute and 40 null-comparison members for the 1.5B decode floor, with prefill extracted prospectively from the same 50 bundles; beta repeats this for 7B; gamma collects ten 1.5B-versus-7B decode ABBA blocks. Their budgeted occupancies, including 20% margin, are approximately 3.14, 3.24, and 2.80 hours. Before those nights, desk work must land the two-slot calibration-bracket session, acceptance-successor machinery, multi-plan/four-cell mint, prefill metric support, three-window regression, frozen campaign packs, and readiness packets. After alpha and beta pass, mint the combined four-cell floor artifact; then run gamma and apply the armwise maximum of the two decode floors plus the separate claim-side interval. For this paper, add a machine-readable and human-readable “nutrition label” renderer and validator, then apply it to every D-117 floor and demonstration result. Finally, conduct a preregistered desk audit of approximately 40 result rows—proposed, not power-derived—from the four nearest reporting systems discussed in the MVP draft, scoring whether each label field can be recovered. This is explicitly a metrology disclosure label, not a carbon label, battery-life estimate, certification, or public cross-device leaderboard.

## Contributions

1. **A falsifiable minimum reporting schema.** A result is complete only if it binds boundary, gross-J/request estimand, workload, phase, physical unit, OS/runtime/model/quantization/tokenizer identity, calibration bracket and status, floor decomposition, claim interval, gate verdict, and custody digest. The validator must reject every deliberately omitted mandatory field.

2. **A comparability decision procedure.** Pairwise comparison is permitted only when label fields establish the same boundary and compatible estimands; mutation tests must refuse boundary substitution, tokenizer-blind J/token ranking, point-repeatability substituted for the operative floor, and uncalibrated cross-boundary ranking.

3. **Five real label cells plus a contrast verdict.** The four D-117 floor cells—1.5B/7B × prefill/decode—and the decode contrast must be rendered directly from governed artifacts, with no hand-copied scientific numbers and byte-linked provenance.

4. **A reporting-practice audit.** Two independent coders apply the frozen rubric to the proposed 40-row literature/leaderboard sample. Report field-completeness rates and agreement; the critique fails if prevailing reporting already supplies the proposed mandatory evidence reliably.

## Experiment plan

Alpha and beta each contain 50 unique science bundles: 10 absolute members and ten four-member A/B/B/A null blocks, using the 128-prompt/512-output workload. Prefill is a preregistered rider over those exact bundles, not borrowed from a decode floor after collection. Gamma contains 40 members in ten ABBA blocks and tests `7B − 1.5B` decode energy.

The historical decode contrast is approximately 141.29 J on the registered phase metric—diagnostic only, not a claim—about 28 times the approximate 5 J practical bar. The prospective value is unknown, but a failure to clear would be scientifically important: the label would show that an apparently large table difference still lacks permission for directional language. Historical 128-token prefill diagnostics give a 5.81 J point contrast, but an uncertainty-adjusted lower edge near 4.0 J; it is therefore marginal, not evidence for a prefill direction. A 256-token arm projects roughly 11.6 J, about 2.3 times the bar, but this is an uncertain extrapolation because no long-prompt 7B corpus exists.

Base paper cost is exactly the three D-117 windows. A fourth, independently calibrated 256-token prefill window is optional for an ICPE-strengthened version only; it needs matching floor cells or a preregistered transport rule and likely about 110 core minutes plus bookends. No extension may be appended to gamma after freeze. Required new harness work is label serialization, completeness/comparability validation, and artifact-to-label rendering. It does not alter the frozen sequential, single-request boundary.

## Hardware and instrument needs

The owned M3 Max is sufficient; the RTX 3080 Ti and Jetsons are irrelevant. The WT310E is **not a dependency** because the label explicitly names the modeled `powermetrics` SoC boundary and withholds wall-energy claims. A borrowed WT310E would enable a later “wall-bridged total” label class, but still would not validate prefill/decode attribution.

## Venue fit and relationship to the MVP

This is an excellent capstone/CSCSU chapter and a credible performance- or sustainable-systems workshop paper. ICPE full-track fit is plausible only with the executable validator, the reporting audit, artifact-quality release, and preferably external adoption or wall-boundary extension; the label idea alone is too modest.

It reuses the MVP draft’s Sections 2–6 nearly intact: related-work gap, calibration, floor composition, fail-closed protocol, and instrument characterization. What is new is the reporting schema, comparability rules, mutation evaluation, audit, and D-117 results presented as worked labels rather than another leaderboard table.

## Risks and kill criteria

Kill it as a standalone paper before spending any extra night if the desk audit shows that the schema merely renames already-standard fields, if reviewers cannot apply the rubric reproducibly, or if the label produces no decision beyond existing paper prose. In that case, retain it as an MVP artifact/section. Do not fund the fourth window unless the 256-token plan has matching floor authority and a conservative projected interval clears 5 J. Failed D-117 windows, missing mint machinery, or unresolved custody bindings delay the paper; they must not be papered over with historical values.

## Relation to Ed’s original goals

This directly serves the energy-honest leaderboard/reporting axis and strengthens the modular harness by defining what every future experimental axis must disclose. It does not advance speculative decoding, MTP, MoE, KV variants, or split inference directly; instead, it supplies the reporting contract those later studies would need to make defensible energy comparisons.
